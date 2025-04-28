from aiogram import types
from utils.defs import extract_batch_id_from_barcode, timestamp_to_date
import requests


from loader import dp


@dp.message_handler()
async def check(message: types.Message):
    kod = message.text
    if kod.isdigit() and len(kod) == 13:
        # await message.answer(f"Siz yuborgan shtrix kod: {kod}")
        batch_id = extract_batch_id_from_barcode(kod)
        url = f'http://localhost:8000/get_batch_info/{batch_id}'
        response = requests.get(url)
        await message.reply(f"Batch info: {batch_id}")
        if response.status_code == 200:
            batch_info = response.json()  # Faraz qilaylik, server JSON formatida javob beradi
            manufacture_date = timestamp_to_date(
                batch_info['manufacture_date'])
            expiry_date = timestamp_to_date(batch_info['expiry_date'])
            answer_message = (
                f"<b>Dori ma'lumotlari:</b>\n\n"
                f"<b>Batch ID:</b> {batch_info['batch_id']}\n"
                f"<b>Dori nomi:</b> {batch_info['medicine_name']}\n"
                f"<b>Ishlab chiqaruvchi nomi:</b> {batch_info['manufacturer_name']}\n"
                f"<b>Ishlab chiqaruvchi manzili:</b> {batch_info['manufacturer_address']}\n"
                f"<b>Distribyutor nomi:</b> {batch_info['distributor_name']}\n"
                f"<b>Distribyutor manzili:</b> {batch_info['distributor_address']}\n"
                f"<b>Apteka manzili:</b> {batch_info['pharmacy_address']}\n"
                f"<b>Ishlab chiqarilgan sana:</b> {manufacture_date}\n"
                f"<b>Muddati tugash sanasi:</b> {expiry_date}\n"
                f"<b>Distribyutor qabul qilganmi:</b> {'✅ Ha' if batch_info['distributor_accepted'] else '❌ Yo‘q'}\n"
                f"<b>Apteka qabul qilganmi:</b> {'✅ Ha' if batch_info['pharmacy_accepted'] else '❌ Yo‘q'}\n"
                f"<b>Sertifikat xeshi:</b> {batch_info['certificate_hash'] or '(Mavjud emas)'}"
            )
            await message.answer(answer_message, parse_mode=types.ParseMode.HTML)
        else:
            await message.reply("So'rovga javob olishda xatolik yuz berdi.")

    else:
        await message.answer("Siz yuborgan textda shtrix kod mavjud emas")
