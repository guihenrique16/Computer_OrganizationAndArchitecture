# Sprint 3 — Controle Inteligente de Sessão de Recarga

Protótipo educacional de gerenciamento de recarga para eletropostos comerciais, desenvolvido com **Raspberry Pi Pico**, **MicroPython** e **Wokwi**.

O projeto foi inspirado no conceito de gerenciamento inteligente de energia da GoodWe e adaptado ao contexto do **ChargeGrid Intelligence**, uma solução voltada ao controle energético e à tarifação de sessões de recarga em estabelecimentos comerciais.

## Objetivo

Simular um controlador que recebe dados de geração e consumo, calcula a potência disponível e decide automaticamente se a sessão de recarga deve ser autorizada, reduzida ou bloqueada.

```text
Potência disponível = Geração - Consumo
```

Além dos três estados obrigatórios, o protótipo inclui:

- modo manual com potenciômetros;
- modo de demonstração automática;
- dois displays LCD I2C;
- cálculo de energia acumulada e custo;
- botão de emergência;
- relé para liberação ou corte da carga;
- representação de dados em decimal, binário e hexadecimal;
- Monitor Serial com informações operacionais.

## Estados da recarga

O carregador solicita até **2500 W**. A potência efetivamente fornecida depende da disponibilidade calculada.

| Condição | Estado | LED | Potência de carga | Relé |
|---|---|---|---:|---|
| Disponível ≥ 2500 W | Recarga autorizada | Verde | 2500 W | Ligado |
| Disponível entre 1 W e 2499 W | Recarga reduzida | Amarelo | Igual à potência disponível | Ligado |
| Disponível ≤ 0 W | Recarga bloqueada | Vermelho | 0 W | Desligado |
| Emergência acionada | Emergência | Vermelho | 0 W | Desligado |

O LED azul representa o carregador energizado. Ele permanece aceso apenas quando o relé libera a recarga.

## Modos de funcionamento

### Modo manual

Os dois potenciômetros simulam geração e consumo, ambos na faixa de **0 a 5000 W**. Ao movimentá-los, o Raspberry Pi Pico lê as entradas analógicas, recalcula a disponibilidade e atualiza LEDs, relé, LCDs e terminal.

### Modo demonstração

A chave seletora ativa uma sequência automática com os três casos exigidos na atividade. Cada situação permanece ativa por cinco segundos.

| Situação | Geração | Consumo | Disponível | Resultado |
|---|---:|---:|---:|---|
| 1 | 4000 W | 1500 W | 2500 W | Recarga autorizada |
| 2 | 1800 W | 1500 W | 300 W | Recarga reduzida |
| 3 | 1000 W | 1800 W | -800 W | Recarga bloqueada |

## Displays

O projeto utiliza dois LCDs 20×4 conectados ao mesmo barramento I2C.

### LCD de dados energéticos — endereço 0x27

Apresenta geração, consumo, potência disponível e estado da recarga.

### LCD da sessão comercial — endereço 0x26

Apresenta potência fornecida ao veículo, energia acumulada em kWh, tarifa simulada de R$ 1,50 por kWh e custo acumulado.

```text
Energia (kWh) = Potência (kW) × Tempo (h)
Custo (R$) = Energia (kWh) × Tarifa (R$/kWh)
```

## Componentes simulados

- 1 Raspberry Pi Pico;
- 3 LEDs de estado: verde, amarelo e vermelho;
- 1 LED azul para representar o carregador;
- 4 resistores de 220 Ω;
- 2 LCDs 20×4 I2C;
- 2 potenciômetros deslizantes;
- 1 botão de emergência;
- 1 módulo relé;
- 1 chave seletora de modo.

## Mapeamento de pinos

| Componente | Pino do Pico | Função |
|---|---:|---|
| LCDs — SDA | GP0 | Dados do barramento I2C |
| LCDs — SCL | GP1 | Clock do barramento I2C |
| LED verde | GP2 | Recarga autorizada |
| LED amarelo | GP3 | Recarga reduzida |
| LED vermelho | GP4 | Bloqueio ou emergência |
| Chave de modo | GP14 | Alternância manual/demonstração |
| Botão de emergência | GP15 | Corte imediato da recarga |
| Relé | GP16 | Liberação da alimentação do carregador |
| Potenciômetro de geração | GP26 / ADC0 | Entrada analógica de geração |
| Potenciômetro de consumo | GP27 / ADC1 | Entrada analógica de consumo |

## Representação de dados

O Monitor Serial apresenta a geração em três sistemas numéricos. Para uma geração de **4000 W**:

```text
Decimal:     4000
Binário:     111110100000
Hexadecimal: FA0
```

## Relação com Arquitetura de Computadores

| Conceito | Aplicação no protótipo |
|---|---|
| Entrada | Potenciômetros, chave seletora e botão de emergência |
| Processamento | Cálculo de potência disponível, estado, energia e custo |
| Memória | Variáveis que armazenam leituras, estado e energia acumulada |
| Saída | LEDs, relé, LCDs e Monitor Serial |
| Conversão de dados | ADC converte sinais analógicos em valores digitais |
| Barramento | I2C permite controlar dois LCDs pelos mesmos fios SDA e SCL |
| Sistemas numéricos | Exibição em decimal, binário e hexadecimal |

## Aplicação em eletropostos comerciais

Em um eletroposto real, a potência disponível varia conforme a geração local e o consumo do estabelecimento. O controlador evita que a recarga ultrapasse a capacidade disponível, reduzindo a potência quando necessário ou bloqueando a sessão em situações críticas.

O cálculo de energia e custo aproxima o protótipo de um sistema comercial, no qual cada sessão precisa registrar os kWh entregues e aplicar uma tarifa ao usuário.

Este projeto é um protótipo educacional. Ele não mede nem controla uma instalação elétrica real.

## Estrutura dos arquivos

```text
Sprint-03/
├── main.py       # Lógica principal do controlador
├── lcd_i2c.py    # Driver dos displays LCD I2C
├── diagram.json  # Circuito do projeto no Wokwi
└── README.md     # Documentação técnica
```

## Como executar no Wokwi

1. Crie um projeto **MicroPython para Raspberry Pi Pico** no Wokwi.
2. Substitua o conteúdo do `diagram.json` pelo arquivo deste repositório.
3. Substitua o `main.py`.
4. Crie o arquivo `lcd_i2c.py` e copie seu conteúdo.
5. Inicie a simulação.
6. Use a chave seletora para alternar entre os modos manual e demonstração.
7. No modo manual, ajuste os potenciômetros.
8. Pressione o botão vermelho ou a tecla **E** para testar a emergência.

Ao iniciar, o Monitor Serial deve identificar os LCDs nos endereços decimais 38 e 39, correspondentes a 0x26 e 0x27:

```text
Dispositivos I2C: [38, 39]
```

## Testes recomendados

- confirmar que somente um LED de estado permanece aceso;
- verificar o ciclo automático das três situações;
- movimentar os potenciômetros no modo manual;
- testar o corte do relé pelo botão de emergência;
- confirmar que o LED azul apaga nos estados bloqueado e emergência;
- verificar que energia e custo aumentam somente durante a recarga;
- conferir os dados dos dois LCDs e do Monitor Serial.
