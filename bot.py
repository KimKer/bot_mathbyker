# Bot de Telegram – Agilidad Mental Matemática (Nivel 3)
# Requiere: python-telegram-bot >= 20
# pip install python-telegram-bot

import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import os

TOKEN = os.getenv("TELEGRAM_TOKEN")



# ------------------ GENERADORES DE EJERCICIOS ------------------

def suma_reagrupacion():
    a = random.randint(100, 999)
    b = random.randint(100, 999)
    return f"{a} + {b}", a + b

def resta_desagrupacion():
    a = random.randint(300, 999)
    b = random.randint(100, a-1)
    return f"{a} - {b}", a - b

def multiplicacion_mixta():
    tipos = [(random.randint(2,9), random.randint(10,99)),
             (random.randint(10,99), random.randint(2,9))]
    a, b = random.choice(tipos)
    return f"{a} × {b}", a * b

def division_corta():
    divisor = random.randint(2,9)
    if random.choice([True, False]):
        dividendo = random.randint(10,999)
        resultado = dividendo / divisor
    else:
        dividendo = round(random.uniform(1,99),1)
        resultado = round(dividendo / divisor,2)
    return f"{dividendo} ÷ {divisor}", resultado

# ------------------ SESIÓN DEL USUARIO ------------------

def crear_sesion():
    ejercicios = []
    for _ in range(10): ejercicios.append(suma_reagrupacion())
    for _ in range(10): ejercicios.append(resta_desagrupacion())
    for _ in range(10): ejercicios.append(multiplicacion_mixta())
    for _ in range(10): ejercicios.append(division_corta())
    random.shuffle(ejercicios)
    return {
        "ejercicios": ejercicios,
        "indice": 0,
        "aciertos": 0
    }

# ------------------ HANDLERS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["sesion"] = crear_sesion()
    await update.message.reply_text(
        "Entrenamiento diario de agilidad mental activado.\n"
        "Responderás 40 ejercicios. Escribe la respuesta numérica."
    )
    await enviar_ejercicio(update, context)

async def enviar_ejercicio(update, context):
    sesion = context.user_data.get("sesion")
    i = sesion["indice"]
    if i >= len(sesion["ejercicios"]):
        await update.message.reply_text(
            f"Entrenamiento finalizado.\n"
            f"Aciertos: {sesion['aciertos']} / 40"
        )
        return
    ejercicio, _ = sesion["ejercicios"][i]
    await update.message.reply_text(f"Ejercicio {i+1}/40: {ejercicio}")

async def respuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion = context.user_data.get("sesion")
    if not sesion:
        return
    i = sesion["indice"]
    _, correcto = sesion["ejercicios"][i]
    try:
        user_resp = float(update.message.text.replace(',', '.'))
        if abs(user_resp - correcto) < 0.01:
            sesion["aciertos"] += 1
            await update.message.reply_text("Correcto")
        else:
            await update.message.reply_text(f"Incorrecto. Respuesta correcta: {correcto}")
    except:
        await update.message.reply_text("Ingresa un número válido")
        return
    sesion["indice"] += 1
    await enviar_ejercicio(update, context)

# ------------------ MAIN ------------------

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respuesta))
    app.run_polling()

if __name__ == '__main__':
    main()

