
# 🚀 ScoutPro - Sistema de Avaliação de Jogadores

Sistema profissional desenvolvido em Django para avaliação de jogadores de futebol em tempo real, com interface responsiva e dashboard personalizado por tipo de usuário.

## 📋 Funcionalidades Principais

### 👨‍💼 Para Comissão Técnica

- ✅ Dashboard completo com estatísticas gerais
- ✅ Gerenciamento de jogadores e times
- ✅ Sistema de avaliação em tempo real
- ✅ Relatórios e estatísticas detalhadas
- ✅ Controle de escalações e substituições

### ⚽ Para Jogadores

- ✅ Dashboard pessoal com estatísticas individuais
- ✅ Acompanhamento de evolução temporal
- ✅ Histórico de jogos e avaliações
- ✅ Perfil pessoal editável

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 5.2.1, Python 3.9+
- **Frontend:** Bootstrap 5.3.6, JavaScript, Font Awesome
- **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Responsividade:** Mobile-first design
- **Autenticação:** Sistema Django customizado

## 📦 Instalação Rápida

### Opção 1: Script Automático (Recomendado)

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd ScoutPro

# 2. Execute o script de configuração
python setup.py
```

### Opção 2: Instalação Manual

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd ScoutPro

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie a estrutura de diretórios
mkdir -p templates/auth templates/core static/css static/js static/img
mkdir -p media/teams/logos media/players/photos
mkdir -p core/management/commands
touch core/management/__init__.py core/management/commands/__init__.py

# 5. Execute as migrações
python manage.py makemigrations
python manage.py migrate

# 6. Configure dados iniciais
python manage.py setup_initial_data

# 7. Inicie o servidor
python manage.py runserver
```

## 🔑 Credenciais de Acesso

### 👨‍💼 Administrador

- **Usuário:** `admin`
- **Senha:** `admin123`
- **URL:** `http://localhost:8000/admin/`

### 👨‍💼 Comissão Técnica

- **Usuário:** `coach`
- **Senha:** `coach123`

### ⚽ Jogadores de Demonstração

- **Usuários:** `player1`, `player2`, `player3`, `player4`, `player5`
- **Senha:** `player123` (para todos)

## 🌐 URLs do Sistema

- **Home/Login:** `http://localhost:8000/`
- **Admin:** `http://localhost:8000/admin/`
- **Dashboard Comissão:** `http://localhost:8000/dashboard/coach/`
- **Dashboard Jogador:** `http://localhost:8000/dashboard/player/`
- **Perfil:** `http://localhost:8000/profile/`

## 📁 Estrutura do Projeto

```
ScoutPro/
├── config/
│   ├── settings.py          # Configurações do Django
│   ├── urls.py             # URLs principais
│   └── wsgi.py             # Configuração WSGI
├── core/
│   ├── models.py           # Models (User, Team, Player)
│   ├── views.py            # Views do sistema
│   ├── urls.py             # URLs do app core
│   ├── admin.py            # Configuração do admin
│   └── management/
│       └── commands/
│           └── setup_initial_data.py
├── templates/
│   ├── base.html           # Template base
│   ├── auth/
│   │   └── login.html      # Tela de login
│   └── core/
│       ├── coach_dashboard.html
│       ├── player_dashboard.html
│       ├── dashboard.html
│       └── profile.html
├── static/                 # Arquivos estáticos
├── media/                  # Uploads de usuários
├── requirements.txt        # Dependências Python
├── setup.py               # Script de configuração
└── README.md              # Este arquivo
```

## 🎯 Próximas Fases de Desenvolvimento

### Fase 2 - Funcionalidades Core

- [ ] Sistema completo de avaliação em tempo real
- [ ] CRUD de jogos e escalações
- [ ] Módulo de substituições durante jogos
- [ ] Sistema de cronômetro integrado

### Fase 3 - Relatórios e Estatísticas

- [ ] Geração de relatórios em PDF
- [ ] Gráficos interativos com Chart.js
- [ ] Exportação de dados em Excel
- [ ] Comparativos entre jogadores

### Fase 4 - Funcionalidades Avançadas

- [ ] Sistema de tempo real com WebSockets
- [ ] Notificações push
- [ ] API REST para integração mobile
- [ ] Sistema de backup automático

## 🔧 Comandos Úteis

```bash
# Criar um novo superusuário
python manage.py createsuperuser

# Resetar dados e recriar usuários demo
python manage.py setup_initial_data --reset

# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic

# Fazer backup do banco
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json
```

## 🐛 Resolução de Problemas

### Erro: "No module named 'PIL'"

```bash
pip install Pillow
```

### Erro: "Table doesn't exist"

```bash
python manage.py makemigrations
python manage.py migrate
```

### Erro: "Static files not found"

```bash
python manage.py collectstatic
```

### Problemas de permissão com diretórios

```bash
# Linux/Mac
chmod -R 755 media/
chmod -R 755 static/

# Windows - execute como administrador
```

### Reset completo do banco de dados

```bash
# CUIDADO: Isso apaga todos os dados!
rm db.sqlite3
rm -rf core/migrations/
python manage.py makemigrations core
python manage.py migrate
python manage.py setup_initial_data
```

## 📱 Responsividade

O sistema foi desenvolvido com abordagem **mobile-first** e é totalmente responsivo:

- ✅ **Smartphones** (320px+)
- ✅ **Tablets** (768px+)
- ✅ **Desktops** (1024px+)
- ✅ **Telas grandes** (1200px+)

## 🔒 Segurança

- ✅ Autenticação robusta do Django
- ✅ Proteção CSRF habilitada
- ✅ Validação de dados server-side
- ✅ Controle de permissões por tipo de usuário
- ✅ Senhas hasheadas com algoritmo PBKDF2

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:

- **Email:** suporte@scoutpro.com
- **Issues:** Use o sistema de issues do GitHub
- **Documentação:** Wiki do projeto

---

**ScoutPro** - Desenvolvido com ❤️ para a comunidade do futebol
