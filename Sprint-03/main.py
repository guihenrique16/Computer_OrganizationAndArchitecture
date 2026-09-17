from machine import Pin, ADC, I2C
from time import sleep, ticks_ms, ticks_diff
from lcd_i2c import LCDI2C


# CONFIGURACOES
POTENCIA_MAXIMA = 5000
POTENCIA_SOLICITADA = 2500
TARIFA_KWH = 1.50

TEMPO_CADA_SITUACAO = 5000
INTERVALO_TERMINAL = 2000


# SITUACOES AUTOMATICAS
situacoes_demo = [
    {
        "numero": 1,
        "geracao": 4000,
        "consumo": 1500
    },
    {
        "numero": 2,
        "geracao": 1800,
        "consumo": 1500
    },
    {
        "numero": 3,
        "geracao": 1000,
        "consumo": 1800
    }
]


# SAIDAS DIGITAIS
led_verde = Pin(2, Pin.OUT)
led_amarelo = Pin(3, Pin.OUT)
led_vermelho = Pin(4, Pin.OUT)

rele_carga = Pin(16, Pin.OUT)

RELE_LIGADO = 0
RELE_DESLIGADO = 1


# ENTRADAS ANALOGICAS
pot_geracao = ADC(26)
pot_consumo = ADC(27)


# ENTRADAS DIGITAIS
# Pressionado = 0
botao_emergencia = Pin(
    15,
    Pin.IN,
    Pin.PULL_UP
)

# 0 = manual
# 1 = demonstracao
chave_modo = Pin(
    14,
    Pin.IN,
    Pin.PULL_DOWN
)



# LCDS
i2c = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1),
    freq=400000
)

print("Dispositivos I2C:", i2c.scan())

lcd_dados = LCDI2C(
    i2c,
    0x27,
    4,
    20
)

lcd_sessao = LCDI2C(
    i2c,
    0x26,
    4,
    20
)


# FUNCOES
def apagar_leds():
    led_verde.off()
    led_amarelo.off()
    led_vermelho.off()


def ler_potencia(adc):
    leitura_adc = adc.read_u16()

    potencia = int(
        leitura_adc
        * POTENCIA_MAXIMA
        / 65535
    )

    return potencia


def definir_estado(disponivel, emergencia):
    apagar_leds()

    if emergencia:
        led_vermelho.on()
        rele_carga.value(RELE_DESLIGADO)

        return "EMERGENCIA", 0

    if disponivel >= POTENCIA_SOLICITADA:
        led_verde.on()
        rele_carga.value(RELE_LIGADO)

        return "AUTORIZADA", POTENCIA_SOLICITADA

    if disponivel > 0:
        led_amarelo.on()
        rele_carga.value(RELE_LIGADO)

        return "REDUZIDA", disponivel

    led_vermelho.on()
    rele_carga.value(RELE_DESLIGADO)

    return "BLOQUEADA", 0


def atualizar_lcd_dados(
    geracao,
    consumo,
    disponivel,
    estado
):
    lcd_dados.escrever_linha(
        0,
        "GERACAO: %d W" % geracao
    )

    lcd_dados.escrever_linha(
        1,
        "CONSUMO: %d W" % consumo
    )

    lcd_dados.escrever_linha(
        2,
        "DISPONIVEL: %d W" % disponivel
    )

    lcd_dados.escrever_linha(
        3,
        "STATUS: " + estado
    )


def atualizar_lcd_sessao(
    potencia_carga,
    energia_kwh,
    custo
):
    lcd_sessao.escrever_linha(
        0,
        "CARGA: %d W" % potencia_carga
    )

    lcd_sessao.escrever_linha(
        1,
        "ENERGIA: %.3f kWh" % energia_kwh
    )

    lcd_sessao.escrever_linha(
        2,
        "TARIFA: R$ %.2f/kWh" % TARIFA_KWH
    )

    lcd_sessao.escrever_linha(
        3,
        "CUSTO: R$ %.2f" % custo
    )


def apresentar_terminal(
    modo,
    numero_situacao,
    geracao,
    consumo,
    disponivel,
    estado,
    potencia_carga,
    energia_kwh,
    custo,
    emergencia
):
    print()
    print("================================")
    print("CONTROLE DE ELETROPOSTO")
    print("================================")
    print("MODO:", modo)

    if modo == "DEMONSTRACAO":
        print("SITUACAO:", numero_situacao)

    print("GERACAO:", geracao, "W")
    print("CONSUMO:", consumo, "W")
    print("DISPONIVEL:", disponivel, "W")
    print("POTENCIA DE CARGA:", potencia_carga, "W")
    print("STATUS:", estado)
    print("EMERGENCIA:", emergencia)
    # print("ENERGIA: %.3f kWh" % energia_kwh)
    # print("TARIFA: R$ %.2f/kWh" % TARIFA_KWH)
    # print("CUSTO: R$ %.2f" % custo)

    print()
    print("REPRESENTACAO DA GERACAO")
    print("Decimal:", geracao)
    print("Binario:", bin(geracao)[2:])
    print("Hexadecimal:", hex(geracao)[2:].upper())
    print("================================")



# INICIALIZACAO
apagar_leds()
rele_carga.value(RELE_DESLIGADO)

lcd_dados.limpar()
lcd_sessao.limpar()

energia_kwh = 0.0

indice_demo = 0
numero_situacao = 0

agora = ticks_ms()
ultimo_calculo = agora
ultima_troca_demo = agora
ultima_exibicao_terminal = agora

modo_anterior = ""



# PROGRAMA PRINCIPAL
while True:
    agora = ticks_ms()

    tempo_decorrido = (
        ticks_diff(agora, ultimo_calculo)
        / 1000
    )

    ultimo_calculo = agora

    emergencia = (
        botao_emergencia.value() == 0
    )

    modo_demo = (
        chave_modo.value() == 1
    )

    if modo_demo:
        modo = "DEMONSTRACAO"

        if modo_anterior != modo:
            indice_demo = 0
            ultima_troca_demo = agora

        elif ticks_diff(
            agora,
            ultima_troca_demo
        ) >= TEMPO_CADA_SITUACAO:

            indice_demo += 1

            if indice_demo >= len(situacoes_demo):
                indice_demo = 0

            ultima_troca_demo = agora

        situacao = situacoes_demo[indice_demo]

        numero_situacao = situacao["numero"]
        geracao = situacao["geracao"]
        consumo = situacao["consumo"]

    else:
        modo = "MANUAL"
        numero_situacao = 0

        geracao = ler_potencia(pot_geracao)
        consumo = ler_potencia(pot_consumo)

    disponivel = geracao - consumo

    estado, potencia_carga = definir_estado(
        disponivel,
        emergencia
    )

    if potencia_carga > 0:
        energia_kwh += (
            potencia_carga
            / 1000
            * tempo_decorrido
            / 3600
        )

    custo = energia_kwh * TARIFA_KWH

    atualizar_lcd_dados(
        geracao,
        consumo,
        disponivel,
        estado
    )

    atualizar_lcd_sessao(
        potencia_carga,
        energia_kwh,
        custo
    )

    if modo != modo_anterior:
        print()
        print("MODO ALTERADO PARA:", modo)

        lcd_dados.limpar()
        lcd_sessao.limpar()

        modo_anterior = modo

    if ticks_diff(
        agora,
        ultima_exibicao_terminal
    ) >= INTERVALO_TERMINAL:

        apresentar_terminal(
            modo,
            numero_situacao,
            geracao,
            consumo,
            disponivel,
            estado,
            potencia_carga,
            energia_kwh,
            custo,
            emergencia
        )

        ultima_exibicao_terminal = agora

    sleep(0.2)