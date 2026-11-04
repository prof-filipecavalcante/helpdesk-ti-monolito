# Desafio: do monólito aos microsserviços

**Disciplina:** Arquitetura de Software · **Prof. Filipe Cavalcante**
**Modalidade:** individual

## A missão

O **HelpDesk TI** funciona, mas é um **monólito**: uma aplicação, um banco e uma implantação.
A empresa cresceu e cada parte do sistema passou a ter um time próprio. A sua missão é
**transformar o HelpDesk em microsserviços**, sem perder nenhuma funcionalidade.

## Como começar

1. No topo deste repositório, clique em **Use this template → Create a new repository**.
2. Crie o repositório na **sua conta**, **público**, com o nome `helpdesk-microsservicos-<seu-nome>`.
3. Rode o monólito antes de mudar qualquer coisa (veja o [README](README.md)) e conheça as telas e as rotas.
4. Entre com as contas de exemplo (senha `Helpdesk2026`): **carla@empresa.com** (técnica) para o fluxo completo e **ana@empresa.com** (solicitante) para ver as permissões. A lista completa está no README, em [Contas de acesso](README.md#contas-de-acesso).

## Onde está hoje (monólito)

```mermaid
flowchart TB
    Tela[Tela do HelpDesk] --> App
    subgraph App[Aplicação única]
        Usuarios[usuarios]
        Inventario[inventario]
        Chamados[chamados]
        Notificacoes[notificacoes]
        Chamados -->|função| Usuarios
        Chamados -->|função| Inventario
        Chamados -->|função| Notificacoes
    end
    App --> BD[(Banco único)]
```

## Aonde você deve chegar

```mermaid
flowchart TB
    Tela[Tela do HelpDesk] --> Gateway[API Gateway]
    Gateway --> SU[Serviço de Usuários]
    Gateway --> SI[Serviço de Inventário]
    Gateway --> SC[Serviço de Chamados]
    SC -->|HTTP| SU
    SC -->|HTTP| SI
    SU --> BU[(Banco de usuários)]
    SI --> BI[(Banco de inventário)]
    SC --> BC[(Banco de chamados)]
    SC -. evento ChamadoAberto .-> Fila[[Fila de eventos]]
    Fila -.-> SN[Serviço de Notificações]
```

As linhas tracejadas são o **bônus**.

## Requisitos obrigatórios

1. **Três serviços separados:** Usuários, Inventário e Chamados. Cada um é um projeto próprio, roda no seu próprio contêiner e pode ser iniciado sozinho.
2. **Um banco por serviço:** nenhum serviço lê ou grava no banco de outro. As chaves estrangeiras entre tabelas de serviços diferentes deixam de existir.
3. **Comunicação pela rede:** o serviço de Chamados confere o técnico e o equipamento chamando os outros serviços por HTTP (por exemplo, `GET /usuarios/{id}`).
4. **Tratamento de falhas:** se Usuários ou Inventário estiverem fora do ar, Chamados responde com um erro claro (por exemplo, 503) em vez de travar. Use um tempo limite (`timeout`) nas chamadas.
5. **API Gateway:** um único ponto de entrada (porta 8000) que encaminha cada rota para o serviço certo. A tela do HelpDesk deve continuar funcionando por ele, sem mudar o endereço.
6. **Tudo sobe com um comando:** `docker compose up --build` inicia todos os serviços, bancos e o gateway.
7. **Mesmas funcionalidades:** abrir, atribuir, mudar status, comentar e ver o painel continuam funcionando, com as mesmas regras (SLA e transições de status).
8. **Segurança mantida:** a versão em microsserviços deve ser tão segura quanto o monólito (veja [SECURITY.md](SECURITY.md)):
   - o login continua funcionando e **todo serviço confere o token** antes de responder (o segredo `JWT_SEGREDO` vem do `.env`, nunca do código);
   - as **permissões por perfil** continuam valendo (o solicitante só vê os próprios chamados, e assim por diante);
   - ao chamar outro serviço, **repasse o token** do usuário (cabeçalho `Authorization`);
   - **só o gateway fica exposto**: os serviços e os bancos não publicam portas para fora do Docker;
   - os testes de segurança continuam passando, adaptados a cada serviço.
9. **README do projeto:** diagrama da nova arquitetura em Mermaid, como rodar e as decisões que você tomou.

## Vídeo de demonstração (obrigatório)

Grave um vídeo de **4 a 6 minutos** mostrando a nova versão em microsserviços funcionando.
Publique no YouTube (como **não listado**) ou no Google Drive (com acesso para quem tiver o link)
e coloque o link no início do seu README.

O vídeo deve mostrar, nesta ordem:

1. **A arquitetura:** o diagrama do seu README, explicando os serviços e como eles conversam.
2. **Tudo subindo:** `docker compose up --build` e, em seguida, `docker compose ps` com todos os contêineres no ar.
3. **O fluxo completo pela tela:** entrar como técnico, abrir um chamado, atribuir, resolver e fechar, tudo passando pelo gateway.
4. **A segurança funcionando:** uma chamada sem token recebendo 401 e um solicitante sem conseguir ver o chamado de outra pessoa.
5. **Bancos separados:** mostre que cada serviço tem o seu banco (por exemplo, os volumes ou os arquivos de cada um).
6. **A falha de um serviço:** pare o Inventário com `docker compose stop inventario` e mostre que:
   - a lista de usuários e de chamados continua funcionando;
   - abrir um chamado com equipamento mostra um erro claro, sem travar o sistema.

   Depois, suba o serviço de novo com `docker compose start inventario`.
7. **O que é novo em relação ao monólito:** explique o que mudou e o que ficou melhor ou mais difícil (por exemplo: cada serviço pode ser publicado sozinho, mas agora existe a rede no meio).
8. **Bônus (se fez):** os eventos chegando ao serviço de Notificações e os testes rodando.

Fale com suas palavras. O vídeo não precisa ter edição: uma gravação de tela com sua voz basta.

## Bônus

- **Notificações por evento:** o serviço de Chamados publica os eventos `ChamadoAberto`, `ChamadoAtribuido` e `ChamadoResolvido` em uma fila (por exemplo, Redis ou RabbitMQ). Um serviço de **Notificações** consome esses eventos e grava os avisos. Se Notificações cair, os chamados continuam sendo abertos.
- **Testes por serviço:** cada serviço com seus próprios testes, rodando no GitHub Actions.
- **Rota de saúde:** cada serviço com `GET /saude`, e o gateway mostrando quais serviços estão no ar.

## Dicas

- Procure no código os comentários `# vira chamada HTTP` e `# vira evento` em `app/chamados/servico.py`. Eles marcam exatamente os pontos que mudam.
- Cada módulo já tem uma porta pública (`servico.py`). Comece separando o módulo que **não depende de ninguém** (Usuários ou Inventário).
- Separe um serviço por vez e teste a cada passo. Não tente separar tudo de uma vez.
- Para o gateway, pode ser um pequeno projeto FastAPI que repassa as requisições com `httpx`, ou um Nginx.
- Para conferir o token em cada serviço, reaproveite o código de `app/auth/` (tokens e dependências). O login fica em um serviço só (por exemplo, Usuários).
- Dentro do Docker Compose, os serviços se chamam pelo nome (por exemplo, `http://usuarios:8000`), não por `localhost`.

## O que o professor vai analisar

| Item | O que será observado |
|---|---|
| Separação | Três serviços independentes, cada um com seu banco |
| Comunicação | Chamadas HTTP entre serviços, com timeout e tratamento de falha |
| Gateway | Ponto único de entrada; a tela funciona por ele |
| Segurança | Token conferido em todos os serviços, permissões mantidas, só o gateway exposto, segredos fora do código |
| Execução | `docker compose up --build` sobe tudo sem ajustes manuais |
| Funcionalidades | Fluxo completo de um chamado funcionando |
| Documentação | README com diagrama, instruções e decisões |
| Vídeo | Roteiro completo, com a falha de um serviço e a explicação do que mudou |
| Histórico | Commits ao longo do trabalho, um serviço por vez, com mensagens claras |
| Bônus | Eventos, testes por serviço e rota de saúde |

## Entrega

Envie ao professor, no prazo combinado em aula:

- o **link do seu repositório**;
- o **link do vídeo** (também no início do README).
