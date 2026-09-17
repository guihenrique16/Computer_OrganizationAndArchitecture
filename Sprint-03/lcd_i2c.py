from time import sleep_ms, sleep_us

class LCDI2C:
    LCD_CLEAR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x06
    LCD_DISPLAY_ON = 0x0C
    LCD_FUNCTION = 0x28

    MASK_RS = 0x01
    MASK_ENABLE = 0x04
    MASK_BACKLIGHT = 0x08

    def __init__(self, i2c, endereco, linhas=4, colunas=20):
        self.i2c = i2c
        self.endereco = endereco
        self.linhas = linhas
        self.colunas = colunas
        self.backlight = self.MASK_BACKLIGHT

        sleep_ms(20)

        self._enviar_inicializacao(0x30)
        sleep_ms(5)

        self._enviar_inicializacao(0x30)
        sleep_us(200)

        self._enviar_inicializacao(0x30)
        self._enviar_inicializacao(0x20)

        self.comando(self.LCD_FUNCTION)
        self.comando(self.LCD_DISPLAY_ON)
        self.comando(self.LCD_CLEAR)
        self.comando(self.LCD_ENTRY_MODE)

        sleep_ms(2)

    def _escrever_i2c(self, valor):
        self.i2c.writeto(
            self.endereco,
            bytes([valor | self.backlight])
        )

    def _pulso_enable(self, valor):
        self._escrever_i2c(valor | self.MASK_ENABLE)
        sleep_us(1)

        self._escrever_i2c(valor & ~self.MASK_ENABLE)
        sleep_us(50)

    def _enviar_inicializacao(self, valor):
        self._pulso_enable(valor)

    def _enviar_byte(self, valor, modo):
        parte_alta = (valor & 0xF0) | modo
        parte_baixa = ((valor << 4) & 0xF0) | modo

        self._pulso_enable(parte_alta)
        self._pulso_enable(parte_baixa)

    def comando(self, valor):
        self._enviar_byte(valor, 0)

        if valor in (self.LCD_CLEAR, self.LCD_HOME):
            sleep_ms(2)

    def escrever_caractere(self, caractere):
        self._enviar_byte(ord(caractere), self.MASK_RS)

    def escrever(self, texto):
        for caractere in str(texto):
            self.escrever_caractere(caractere)

    def limpar(self):
        self.comando(self.LCD_CLEAR)

    def posicionar(self, coluna, linha):
        enderecos = [0x00, 0x40, 0x14, 0x54]
        endereco_memoria = enderecos[linha] + coluna
        self.comando(0x80 | endereco_memoria)

    def escrever_linha(self, linha, texto):
        texto = str(texto)[:self.colunas]
        texto = texto + (" " * (self.colunas - len(texto)))

        self.posicionar(0, linha)
        self.escrever(texto)

    def escrever_linha(self, linha, texto):
        texto = str(texto)
        texto = (texto + (" " * self.colunas))[:self.colunas]

        self.posicionar(0, linha)
        self.escrever(texto)