// Tela do HelpDesk. Todo texto vindo da API passa por esc() antes de ir para o HTML,
// para impedir que um título como <script> seja executado (XSS).
"use strict";
const API = "";  // em microsserviços, continua vazio: a tela é servida pelo gateway
const $ = (id) => document.getElementById(id);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (s) => new Date(s).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
const ROTULO = { aberto: "aberto", em_atendimento: "em atendimento", resolvido: "resolvido", fechado: "fechado" };

let token = null, eu = null, usuarios = [];
try { token = sessionStorage.getItem("token"); } catch (e) { token = null; }

async function req(metodo, caminho, corpo) {
  const cab = { "Content-Type": "application/json" };
  if (token) cab.Authorization = "Bearer " + token;
  const r = await fetch(API + caminho, { method: metodo, headers: cab, body: corpo ? JSON.stringify(corpo) : undefined });
  const dados = await r.json().catch(() => ({}));
  if (r.status === 401 && caminho !== "/auth/login") { sair(); throw new Error("Sessão expirada. Entre novamente."); }
  if (!r.ok) throw new Error(typeof dados.detail === "string" ? dados.detail : "Dados inválidos (" + r.status + ").");
  return dados;
}

function guardarToken(t) { token = t; try { t ? sessionStorage.setItem("token", t) : sessionStorage.removeItem("token"); } catch (e) {} }
function sair() { guardarToken(null); eu = null; mostrar(false); }
function mostrar(logado) {
  $("tela-login").hidden = logado; $("tela-sistema").hidden = !logado; $("barra").hidden = !logado;
}
const nome = (id) => (usuarios.find((u) => u.id === id) || {}).nome || "—";
const equipe = () => eu && (eu.perfil === "tecnico" || eu.perfil === "admin");

async function carregar() {
  $("erro").textContent = "";
  eu = await req("GET", "/auth/eu");
  $("quem").textContent = eu.nome + " (" + eu.perfil + ")";
  const [lista, ativos, chamados, painel, avisos] = await Promise.all([
    req("GET", "/usuarios"), req("GET", "/ativos"), req("GET", "/chamados"), req("GET", "/chamados/painel"), req("GET", "/notificacoes"),
  ]);
  usuarios = lista;
  const ps = painel.por_status;
  $("kpis").innerHTML = [["Total", painel.total], ["Abertos", ps.aberto || 0], ["Em atendimento", ps.em_atendimento || 0],
    ["Resolvidos", (ps.resolvido || 0) + (ps.fechado || 0)], ["Atrasados", painel.atrasados]]
    .map(([t, v]) => `<div class="kpi"><small>${esc(t)}</small><b>${esc(v)}</b></div>`).join("");
  const tecnicos = usuarios.filter((u) => u.perfil === "tecnico");
  $("lista").innerHTML = chamados.map((c) => `<tr>
    <td>${esc(c.id)}</td><td><b>${esc(c.titulo)}</b><br><small>${esc(nome(c.solicitante_id))}</small></td>
    <td class="p-${esc(c.prioridade)}">${esc(c.prioridade)}</td>
    <td><span class="pill s-${esc(c.status)}">${esc(ROTULO[c.status])}</span></td>
    <td>${c.tecnico_id ? esc(nome(c.tecnico_id)) : "—"}</td><td>${esc(fmt(c.prazo_sla))}</td>
    <td><div class="acoes">${acoes(c, tecnicos)}</div></td></tr>`).join("") || `<tr><td colspan="7"><small>Nenhum chamado.</small></td></tr>`;
  $("avisos").innerHTML = avisos.slice().reverse().slice(0, 6).map((a) =>
    `<div class="aviso"><b>${esc(a.tipo)}</b><br>${esc(a.mensagem)}<small>${esc(fmt(a.criada_em))}</small></div>`).join("") || "<small>Nenhuma notificação.</small>";
  $("ativo").innerHTML = `<option value="">Nenhum</option>` + ativos.map((a) => `<option value="${esc(a.id)}">${esc(a.patrimonio)} · ${esc(a.descricao)}</option>`).join("");
}

function acoes(c, tecnicos) {
  const botao = (acao, texto, extra = "") => `<button type="button" data-acao="${acao}" data-id="${esc(c.id)}" ${extra}>${esc(texto)}</button>`;
  if (equipe() && c.status === "aberto")
    return `<select id="t${esc(c.id)}" aria-label="Técnico">${tecnicos.map((t) => `<option value="${esc(t.id)}">${esc(t.nome)}</option>`).join("")}</select>` + botao("atribuir", "Atribuir");
  if (equipe() && c.status === "em_atendimento") return botao("resolvido", "Resolver");
  if (c.status === "resolvido" && (equipe() || c.solicitante_id === eu.id))
    return botao("fechado", "Fechar") + botao("em_atendimento", "Reabrir", 'class="sec"');
  return "";
}

async function acao(f) { try { await f(); await carregar(); } catch (e) { $("erro").textContent = e.message; } }

$("lista").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-acao]");
  if (!b) return;
  const id = Number(b.dataset.id);
  if (b.dataset.acao === "atribuir") acao(() => req("PATCH", `/chamados/${id}/atribuir`, { tecnico_id: Number($("t" + id).value) }));
  else acao(() => req("PATCH", `/chamados/${id}/status`, { status: b.dataset.acao }));
});

$("novo").addEventListener("submit", (e) => {
  e.preventDefault();
  acao(() => req("POST", "/chamados", {
    titulo: $("titulo").value, descricao: $("descricao").value, prioridade: $("prioridade").value,
    ativo_id: $("ativo").value ? Number($("ativo").value) : null,
  }));
});

$("tela-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("erro-login").textContent = "";
  try {
    const r = await req("POST", "/auth/login", { email: $("email").value, senha: $("senha").value });
    guardarToken(r.access_token); $("senha").value = "";
    mostrar(true); await carregar();
  } catch (err) { $("erro-login").textContent = err.message; }
});

$("sair").addEventListener("click", sair);

if (token) { mostrar(true); carregar().catch((e) => { $("erro").textContent = e.message; }); } else { mostrar(false); }
