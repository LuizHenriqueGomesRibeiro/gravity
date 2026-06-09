# Gravity

Simulador interativo de gravidade em 2D, escrito em Python com `tkinter`.

O projeto permite criar corpos celestes, visualizar orbitas estimadas, pausar a simulacao, controlar a camera com zoom e pan, e acompanhar a dinamica gravitacional com colisoes e fusoes de corpos.

## Visao geral

O ponto de entrada principal e [`gravity.py`](./gravity.py), que instancia [`GravityGame`](./gravity_sim/game.py).

A aplicacao e organizada em camadas:

- [`gravity_sim/game.py`](./gravity_sim/game.py) coordena o ciclo principal do jogo
- [`gravity_sim/core/physics.py`](./gravity_sim/core/physics.py) calcula a gravidade, colisoes e orbitas
- [`gravity_sim/core/camera.py`](./gravity_sim/core/camera.py) converte coordenadas de mundo e tela
- [`gravity_sim/input/handlers.py`](./gravity_sim/input/handlers.py) trata mouse e teclado
- [`gravity_sim/rendering/renderer.py`](./gravity_sim/rendering/renderer.py) desenha a cena no canvas
- [`gravity_sim/models/body.py`](./gravity_sim/models/body.py) define o modelo dos corpos celestes

## Funcionalidades

- Simulacao gravitacional em 2D
- Pan e zoom da camera
- Criacao interativa de planetas por arrasto tipo `slingshot`
- Visualizacao de trajetoria prevista antes da criacao do corpo
- Criacao de sistemas binarios
- Orbita automatica em torno de um corpo dominante ou do centro de massa
- Rastreamento de corpo selecionado ou do centro de massa
- Trilhas historicas dos corpos
- HUD com informacoes de camera, tempo, massa, gravidade superficial e velocidade
- Colisoes com fusao de corpos

## Requisitos

### Obrigatorios para o simulador principal

- Python 3.12 ou superior
- `tkinter`

### Dependencias opcionais

O arquivo [`gravity_sim/models/fluid_body.py`](./gravity_sim/models/fluid_body.py) usa:

- `taichi`
- `numpy`

Esse modulo nao participa do loop principal da simulacao atual, mas esta disponivel no projeto.

## Instalacao

### 1. Criar e ativar um ambiente virtual

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows `cmd`:

```bat
.venv\Scripts\activate.bat
```

### 2. Instalar dependencias

O simulador principal nao precisa de bibliotecas externas alem do `tkinter`.

Se quiser usar o modulo `FluidBody`, instale:

```bash
pip install taichi numpy
```

## Como executar

```bash
python gravity.py
```

Isso abre a janela do simulador com a interface grafica.

## Controles

### Camera

- Scroll do mouse: zoom
- Botao do meio pressionado e arrasto: pan

### Simulacao

- `P`: pausar/despausar
- `H`: mostrar/ocultar trilhas
- `,` ou `<`: diminuir a velocidade do tempo
- `.` ou `>`: aumentar a velocidade do tempo

### Criacao de corpos

- Clique esquerdo e arraste: define direcao e intensidade do lancamento
- Soltar o mouse nao cria o corpo imediatamente
- `Enter`: cria o corpo no ponto inicial do arrasto
- `Delete`: cancela a criacao em andamento

### Ajustes do corpo em criacao

- `W`: aumenta a velocidade do lancamento
- `S`: reduz a velocidade do lancamento
- `A`: gira o vetor de velocidade para um lado
- `D`: gira o vetor de velocidade para o outro
- `Q`: reduz massa e raio do corpo
- `E`: aumenta massa e raio do corpo

### Orbitas e rastreamento

- `O`: calcula velocidade orbital em torno do corpo dominante proximo
- `C`: calcula velocidade orbital em torno do centro de massa
- `[` e `]`: alternam o alvo orbital entre corpos disponiveis e centro de massa
- Duplo clique esquerdo: rastreia o corpo clicado
- Duplo clique esquerdo sobre o centro de massa: rastreia o centro de massa

### Sistema binario

- `B`: cria um sistema binario igual
- `Shift + B`: cria um sistema binario com companheiro menor
- `Z`: reduz a separacao do binario
- `X`: aumenta a separacao do binario

## Como a simulacao funciona

### Modelo fisico

O motor gravitacional usa:

- constante gravitacional do jogo `G_world = 1.0`
- passo base de simulacao `dt = 0.016`
- integracao com subpassos adaptativos para estabilidade numerica

Os corpos sao atualizados por aceleracao gravitacional mutua, exceto fragmentos, que sentem apenas os corpos principais.

### Colisoes

Quando dois corpos se sobrepoem, o motor avalia a energia cinetica relativa e a compara com uma estimativa de energia de ligacao gravitacional.

Com base nessa razao, a colisao pode resultar em:

- fusao suave
- fusao com perda parcial de massa
- fusao destrutiva em colisoes de alta energia

No estado atual do codigo, a geracao de fragmentos e o rompimento por efeito de mare estao desativados internamente, mesmo que existam constantes e estruturas preparadas para isso.

### Trilhas e orbitas

- Trilhas reais sao armazenadas em uma `deque` por corpo
- Trilhas simuladas sao recalculadas para prever a trajetoria de lancamento
- A trajetoria orbital usa a aproximacao de orbita circular tangencial ao alvo selecionado

## Estrutura do projeto

```text
gravity/
|-- gravity.py
|-- README.md
`-- gravity_sim/
    |-- game.py
    |-- core/
    |   |-- camera.py
    |   `-- physics.py
    |-- input/
    |   `-- handlers.py
    |-- models/
    |   |-- body.py
    |   `-- fluid_body.py
    `-- rendering/
        `-- renderer.py
```

## Principais classes

### `GravityGame`

Responsavel por:

- inicializar a janela
- criar o canvas
- manter o estado global da simulacao
- executar o loop principal

### `PhysicsEngine`

Responsavel por:

- atualizar posicoes e velocidades
- detectar colisoes
- calcular centro de massa
- estimar velocidade orbital
- simular trajetorias de pre-visualizacao

### `Camera`

Responsavel por:

- converter coordenadas mundo/tela
- aplicar zoom com foco no ponteiro
- aplicar pan

### `InputHandler`

Responsavel por:

- ler mouse e teclado
- controlar estado de criacao de corpos
- criar corpos, binarios e orbitas
- atualizar a selecao e o corpo em foco

### `Renderer`

Responsavel por:

- desenhar grade
- desenhar trilhas
- desenhar corpos
- desenhar preview do lancamento
- desenhar HUD e dicas de controle

### `CelestialBody`

Modelo de dados do corpo celeste com:

- posicao
- velocidade
- massa e raio do jogo
- massa e raio reais
- cor
- estado fixo ou fragmento
- trilha historica

## Observacoes importantes

- O simulador e escrito para interface grafica e nao possui CLI dedicado.
- Nao ha arquivo `requirements.txt` no repositorio atual.
- O modulo `FluidBody` e separado e experimental, nao sendo usado pelo jogo principal.
- Os valores fisicos do jogo e os valores reais nao sao a mesma coisa: o jogo usa unidades arbitrarias para a dinamica e guarda massa/raio reais apenas para exibicao e calculo de gravidade superficial no HUD.

## Proximos passos sugeridos

1. Adicionar um `requirements.txt` ou `pyproject.toml`
2. Incluir capturas de tela do simulador no `README`
3. Criar uma secao de perguntas frequentes com dicas de uso
4. Documentar o modulo `FluidBody` separadamente, se ele for mesmo parte da proposta do projeto

