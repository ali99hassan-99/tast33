from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext
import os
import pandas as pd

ADMIN_USER_ID = 917127027  # معرف المدير
EXCEL_FILE = "user_data.xlsx"

# التحقق من وجود ملف Excel أو إنشاؤه
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(
        columns=["UserID", "Name", "FatherName", "GrandFatherName", "MotherName", "MotherFatherName", "BirthProvince",
                 "AdditionalInfo"])
    df.to_excel(EXCEL_FILE, index=False)


# عندما يبدأ المستخدم التفاعل مع البوت
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "للبحث في منصة مظلتي، أرسل المعلومات التالية:\n"
        "الاسم:\nاسم الأب:\nاسم الجد:\nاسم الأم:\nاسم أب الأم:\nمحافظة الولادة:"
    )


# معالجة الرسائل من المستخدمين
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    # إذا كانت الرسالة من المدير، لا توجد حاجة للتحقق من التنسيق
    if user_id == ADMIN_USER_ID:
        # إذا كانت الرسالة تحتوي على معرف المستخدم في السطر الأول، نقوم بإرسال الرد
        lines = text.split("\n")
        if len(lines) < 2:
            await update.message.reply_text(
                "الرسالة يجب أن تحتوي على معرف المستخدم في السطر الأول ونص في الأسطر التالية.")
            return

        user_id_str = lines[0].strip()
        if not user_id_str.isdigit():
            await update.message.reply_text("المعرف في السطر الأول غير صالح.")
            return

        target_user_id = int(user_id_str)

        try:
            # إذا كانت الرسالة تحتوي على صورة
            if update.message.photo:
                photo_file = update.message.photo[-1].file_id  # الحصول على آخر صورة مرفقة
                caption = "\n".join(lines[1:])
                await context.bot.send_photo(chat_id=target_user_id, photo=photo_file, caption=caption)
            else:  # إذا كانت الرسالة نصًا
                await context.bot.send_message(chat_id=target_user_id, text="\n".join(lines[1:]))

            await update.message.reply_text("تم إرسال الرسالة/الصورة بنجاح إلى الشخص المحدد.")
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء إرسال الرسالة: {str(e)}")

        return

    # معالجة الرسائل من المستخدمين العاديين
    lines = text.split("\n")
    if len(lines) < 6:
        await update.message.reply_text("يرجى إرسال جميع المعلومات المطلوبة بالتنسيق الصحيح (على الأقل 6 أسطر).")
        return

    try:
        # استخراج البيانات
        name = lines[0].split(":", 1)[1].strip() if ":" in lines[0] else "غير متوفر"
        father_name = lines[1].split(":", 1)[1].strip() if ":" in lines[1] else "غير متوفر"
        grandfather_name = lines[2].split(":", 1)[1].strip() if ":" in lines[2] else "غير متوفر"
        mother_name = lines[3].split(":", 1)[1].strip() if ":" in lines[3] else "غير متوفر"
        mother_father_name = lines[4].split(":", 1)[1].strip() if ":" in lines[4] else "غير متوفر"
        birth_province = lines[5].split(":", 1)[1].strip() if ":" in lines[5] else "غير متوفر"

        # إذا كان هناك معلومات إضافية
        additional_info = "\n".join(lines[6:]) if len(lines) > 6 else ""

        new_data = {
            "UserID": user_id,
            "Name": name,
            "FatherName": father_name,
            "GrandFatherName": grandfather_name,
            "MotherName": mother_name,
            "MotherFatherName": mother_father_name,
            "BirthProvince": birth_province,
            "AdditionalInfo": additional_info,
        }

        # تخزين البيانات في Excel
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        # إعادة توجيه الرسالة إلى المدير
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"تم استلام رسالة جديدة من المستخدم {user_id}:\n\n" + text
        )

        # إرسال تأكيد للمستخدم
        await update.message.reply_text("تم استلام معلوماتك وسيتم مراجعتها.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء معالجة البيانات: {str(e)}")


# عندما يرد المدير على المستخدمين
async def handle_reply(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # التأكد إذا كان المرسل هو المدير
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("فقط المدير يمكنه الرد على الرسائل.")
        return

    # الرد على رسالة تحتوي على معرف المستخدم
    text = update.message.text.split("\n")
    if len(text) < 2:
        await update.message.reply_text("الرسالة يجب أن تحتوي على معرف المستخدم في السطر الأول ونص في الأسطر التالية.")
        return

    user_id_str = text[0].strip()
    if not user_id_str.isdigit():
        await update.message.reply_text("المعرف في السطر الأول غير صالح.")
        return

    target_user_id = int(user_id_str)

    try:
        # إذا كانت الرسالة تحتوي على صورة
        if update.message.photo:
            photo_file = update.message.photo[-1].file_id  # الحصول على آخر صورة مرفقة
            caption = "\n".join(text[1:])
            await context.bot.send_photo(chat_id=target_user_id, photo=photo_file, caption=caption)
        else:  # إذا كانت نصًا
            await context.bot.send_message(chat_id=target_user_id, text="\n".join(text[1:]))

        await update.message.reply_text("تم إرسال الرسالة/الصورة بنجاح إلى الشخص المحدد.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء إرسال الرسالة: {str(e)}")


def main():
    app = ApplicationBuilder().token("7553057586:AAEY5Uzj0Bqhf6H0uyYQbeXMMtETrVAfRCI").build()

    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("/start"), start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.REPLY & filters.ALL, handle_reply))

    print("البوت يعمل...")
    app.run_polling()


if __name__ == "__main__":
    main()
