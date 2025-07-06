
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json, random, os
from keep_alive import keep_alive

TOKEN = os.environ.get("BOT_TOKEN")
asked_questions = {}
score = {}

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score[user_id] = {"correct": 0, "total": 0}
    asked_questions[user_id] = set()
    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    unused = [q for q in questions if q["question"] not in asked_questions[user_id]]
    if not unused:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="सर्व प्रश्न झाले! ✅")
        return
    question = random.choice(unused)
    asked_questions[user_id].add(question["question"])
    context.user_data["current_question"] = question

    options = [InlineKeyboardButton(opt, callback_data=opt) for opt in question["options"]]
    reply_markup = InlineKeyboardMarkup.from_column(options)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=question["question"], reply_markup=reply_markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    question = context.user_data.get("current_question")
    answer = query.data

    score[user_id]["total"] += 1
    if answer == question["answer"]:
        score[user_id]["correct"] += 1
        reply = f"✅ बरोबर!

{question['explanation']}"
    else:
        reply = f"❌ चूक! योग्य उत्तर: {question['answer']}

{question['explanation']}"

    await query.edit_message_text(text=reply)
    await ask_question(update, context)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_answer))
    app.run_polling()
