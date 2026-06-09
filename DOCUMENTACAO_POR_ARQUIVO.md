# Documentacao dos arquivos Python

Este documento descreve a funcao de cada arquivo `.py` do sistema Gravity.

## Resumo geral

O projeto e dividido em:

- ponto de entrada da aplicacao
- motor de fisica
- camera
- entrada do usuario
- renderizacao
- modelos de dados

## [gravity.py](./gravity.py)

### Funcao

E o ponto de entrada do projeto.

### O que faz

- importa `GravityGame`
- verifica se o arquivo foi executado diretamente
- instancia a aplicacao

### Papel no sistema

Este arquivo nao contem logica de simulacao. Ele apenas inicia o jogo grafico.

---

## [gravity_sim/__init__.py](./gravity_sim/__init__.py)

### Funcao

Marca `gravity_sim` como pacote Python.

### O que faz

- nao expoe logica propria
- permite que os modulos internos sejam importados como pacote

### Papel no sistema

Serve como arquivo de inicializacao do pacote.

---

## [gravity_sim/game.py](./gravity_sim/game.py)

### Funcao

Define a classe principal da aplicacao, `GravityGame`.

### O que faz

- cria a janela Tkinter
- cria o canvas de desenho
- inicializa o estado global do jogo
- instancia os subsistemas de camera, fisica, entrada e renderizacao
- executa o loop principal da simulacao

### Responsabilidades principais

- controlar pausa e estado geral
- manter a lista de corpos celestes
- atualizar a camera quando um corpo e rastreado
- chamar a fisica e o renderer a cada frame

### Papel no sistema

E o centro de orquestracao do simulador. Todo o restante depende dele.

---

## [gravity_sim/core/__init__.py](./gravity_sim/core/__init__.py)

### Funcao

Explicita as principais classes da camada `core`.

### O que faz

- exporta `PhysicsEngine`
- exporta `Camera`

### Papel no sistema

Facilita importacoes do tipo `from gravity_sim.core import Camera`.

---

## [gravity_sim/core/camera.py](./gravity_sim/core/camera.py)

### Funcao

Implementa a camera 2D da simulacao.

### O que faz

- converte coordenadas do mundo para a tela
- converte coordenadas da tela para o mundo
- aplica zoom com foco no cursor
- aplica pan com deslocamento
- ajusta tamanho da viewport quando a janela redimensiona

### Responsabilidades principais

- manter o ponto central observado
- controlar o nivel de aproximacao
- garantir que interacoes com mouse correspondam ao espaco fisico

### Papel no sistema

E a ponte entre o espaco fisico da simulacao e o desenho na interface.

---

## [gravity_sim/core/physics.py](./gravity_sim/core/physics.py)

### Funcao

Implementa o motor de fisica gravitacional.

### O que faz

- calcula aceleracao gravitacional entre corpos
- atualiza posicoes e velocidades por integracao numerica
- trata colisões e fusoes
- calcula centro de massa
- estima velocidade orbital
- gera trajetorias simuladas de prevencao/preview
- identifica o corpo dominante ou o corpo mais proximo

### Responsabilidades principais

- manter a simulacao fisicamente consistente dentro das regras do jogo
- lidar com estabilidade numerica usando subpassos
- definir comportamento em colisao

### Observacoes

- a geracao de fragmentos esta desativada no estado atual
- o rompimento por efeito de mar e esta desativado no estado atual
- o motor usa unidades de jogo, nao unidades astronomicas reais, embora guarde massa e raio reais para exibicao

### Papel no sistema

E o componente mais importante da simulacao. Tudo o que se move ou colide passa por aqui.

---

## [gravity_sim/input/__init__.py](./gravity_sim/input/__init__.py)

### Funcao

Explicita a camada de entrada do usuario.

### O que faz

- exporta `InputHandler`

### Papel no sistema

Ajuda a organizar a camada de eventos de mouse e teclado.

---

## [gravity_sim/input/handlers.py](./gravity_sim/input/handlers.py)

### Funcao

Gerencia toda a interacao do usuario com a aplicacao.

### O que faz

- interpreta eventos de mouse e teclado
- controla pan e zoom por mouse
- controla criacao de corpos por arrasto
- cria planetas ao pressionar `Enter`
- cancela criacao com `Delete`
- ajusta massa, raio, velocidade e direcao do corpo em criacao
- configura orbitas automaticas
- cria sistemas binarios
- controla pausa e exibicao de trilhas
- atualiza o corpo sob o cursor

### Responsabilidades principais

- transformar interacoes humanas em comandos para o simulador
- manter o estado temporario de criacao de corpos
- coordenar o fluxo de lancamento antes da criacao final

### Papel no sistema

E a interface de manipulacao da simulacao. Todo comando do usuario passa por este arquivo.

---

## [gravity_sim/models/__init__.py](./gravity_sim/models/__init__.py)

### Funcao

Explicita os modelos de dados do sistema.

### O que faz

- exporta `CelestialBody`

### Papel no sistema

Facilita o uso do modelo principal em outros modulos.

---

## [gravity_sim/models/body.py](./gravity_sim/models/body.py)

### Funcao

Define o modelo de dados dos corpos celestes.

### O que faz

- armazena nome, posicao, velocidade, massa, raio e cor
- armazena propriedades reais como massa e raio fisicos
- marca se o corpo e fixo ou fragmento
- guarda trilha historica em uma `deque`

### Responsabilidades principais

- representar um objeto fisico dentro da simulacao
- servir como unidade basica de gravidade, colisao e renderizacao

### Papel no sistema

E a estrutura de dados central usada pelo motor de fisica e pelo renderer.

---

## [gravity_sim/models/fluid_body.py](./gravity_sim/models/fluid_body.py)

### Funcao

Implementa um corpo fluidico experimental usando Taichi.

### O que faz

- cria particulas distribuidas em uma area circular
- aplica gravidade simples nas particulas
- atualiza posicoes e velocidades em kernels Taichi
- disponibiliza as posicoes atuais em formato NumPy

### Responsabilidades principais

- simular um corpo como conjunto de particulas
- servir como base para experimentos com fisica de fluidos ou corpos deformaveis

### Observacoes

- este modulo nao e usado pelo loop principal do jogo
- ele depende de `taichi` e `numpy`

### Papel no sistema

E um modulo auxiliar e experimental, separado do simulador principal.

---

## [gravity_sim/rendering/__init__.py](./gravity_sim/rendering/__init__.py)

### Funcao

Explicita a camada de renderizacao.

### O que faz

- exporta `Renderer`

### Papel no sistema

Organiza a importacao da camada visual.

---

## [gravity_sim/rendering/renderer.py](./gravity_sim/rendering/renderer.py)

### Funcao

Desenha a simulacao na tela.

### O que faz

- limpa o canvas a cada frame
- desenha grade de referencia
- desenha trilhas reais e simuladas
- desenha corpos celestes
- desenha o centro de massa
- desenha a linha de lancamento e a previsao de orbita
- desenha preview do sistema binario
- desenha o HUD com informacoes de estado e controles

### Responsabilidades principais

- transformar o estado numerico da simulacao em interface visual
- mostrar informacoes de apoio para o usuario

### Papel no sistema

E o modulo responsavel por toda a representacao grafica do simulador.

---

## Fluxo de execucao

1. `gravity.py` inicia a aplicacao
2. `GravityGame` cria janela, canvas e subsistemas
3. `InputHandler` registra os eventos do usuario
4. `PhysicsEngine` atualiza a simulacao
5. `Renderer` redesenha a interface a cada frame
6. `Camera` ajusta o que e visivel na tela

## Conclusao

Cada arquivo tem uma responsabilidade clara:

- `gravity.py` inicia
- `game.py` coordena
- `physics.py` calcula
- `camera.py` posiciona a visao
- `handlers.py` recebe a interacao do usuario
- `renderer.py` mostra o resultado
- `body.py` modela os corpos
- `fluid_body.py` oferece uma alternativa experimental

Se quiser, este documento pode ser convertido em uma versao mais formal, com linguagem academica, para entrega da faculdade.

