# Segurança

Este projeto é didático, mas segue práticas de segurança reais. Esta página
explica o que já está protegido e o que fica como responsabilidade de quem
for colocar o sistema em produção.

## O que está protegido

| Risco | Proteção |
|---|---|
| Acesso sem login | Todas as rotas, exceto `/auth/login`, `/saude` e a tela, exigem token JWT (`Authorization: Bearer ...`). |
| Senhas vazadas do banco | Senhas guardadas só como hash **scrypt** com sal aleatório. A senha nunca é salva nem devolvida pela API. |
| Adivinhar senhas | Bloqueio temporário após 5 tentativas erradas (por e-mail e endereço). Mensagem igual para e-mail inexistente e senha errada. |
| Token falsificado | Token assinado (HS256) com segredo do servidor, com validade, emissor e algoritmo fixos (tokens `alg: none` são recusados). |
| Ver ou mexer no que não é seu | Permissões por perfil: o solicitante só vê os próprios chamados e notificações; só técnicos e administradores atribuem e resolvem; só administradores criam usuários. |
| Agir em nome de outra pessoa | O solicitante e o autor do comentário vêm do token, não do corpo da requisição. Campos extras são recusados. |
| Descobrir o que existe | Chamado de outra pessoa responde "não encontrado" (404), sem revelar que existe. A lista de usuários não mostra e-mails. |
| XSS na tela | Todo texto vindo da API é escapado antes de entrar no HTML; não há scripts embutidos na página; política CSP só permite scripts do próprio servidor. |
| Clickjacking e outros | Cabeçalhos `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`. |
| Dados enormes | Limites de tamanho em todos os campos e corpo da requisição limitado a 64 KB. |
| SQL injection | Acesso ao banco só pelo SQLAlchemy, com parâmetros (sem SQL montado com texto). |
| Erros que vazam detalhes | Erros de banco respondem com mensagem genérica. |
| Dependências vulneráveis | Versões fixas, `pip-audit` no GitHub Actions a cada envio e Dependabot semanal. |
| Contêiner | Roda como usuário sem privilégios, sistema de arquivos somente leitura, sem capacidades extras, porta exposta só em `127.0.0.1`. |
| Segredos no código | Segredos só por variável de ambiente (`.env`, fora do Git). |

## Antes de usar em produção

- Defina `JWT_SEGREDO` com pelo menos 32 caracteres aleatórios.
- Rode com `DADOS_EXEMPLO=0` (os usuários de exemplo têm senha conhecida) e `DOCS=0`.
- Coloque o sistema atrás de HTTPS (por exemplo, um proxy reverso com certificado).
- Troque o SQLite por um banco gerenciado (PostgreSQL) com backup.
- O limite de tentativas de login fica em memória: com várias instâncias, use um armazenamento compartilhado (Redis).

## Como relatar um problema

Encontrou uma falha? Não abra uma issue pública: envie os detalhes diretamente ao professor.
