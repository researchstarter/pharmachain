from aiogram import types
import requests
from loader import dp
import io
import tempfile
import os
from pyzbar.pyzbar import decode
from PIL import Image
from utils.defs import extract_batch_id_from_barcode, timestamp_to_date


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Rasmdan faylni olish
    photo = message.photo[-1]
    file = await photo.download(destination=io.BytesIO())

    # Faylni vaqtincha saqlash
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    # Rasmni o'qish
    img = Image.open(temp_file_path)
    result = decode(img)

    # Natijani foydalanuvchiga yuborish
    if result:
        code = result[0].data.decode('utf-8')  # Shtrix kodni o'qing
        batch_id = extract_batch_id_from_barcode(code)
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
        await message.reply("Shtrix kod topilmadi.")

    # Vaqtincha faylni o'chirish
    os.remove(temp_file_path)
