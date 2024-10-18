import telebot
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import string
import requests

# বটের টোকেন এবং ইউটিউব API কী
bot = telebot.TeleBot('7768232321:AAEIxiScxQfadADzTGzicsyJ56oDxhfkl1U')
YOUTUBE_API_KEY = 'AIzaSyD5FPM6DiFItiLUSgmqq7u3iDMV-2hEPpI'
CHANNEL_ID = 'UCL-ROLDzcdcId5b8ilSssNA'

# ইনপুট সংরক্ষণের জন্য একটি dictionary ব্যবহার করা হবে
user_data = {}

# ৮ অক্ষরের র্যান্ডম ট্রানজেকশন আইডি তৈরি ফাংশন
def generate_transaction_id():
    return ''.join(random.choices(string.ascii_uppercase, k=8))

# ইউজারের সাবস্ক্রিপশন চেক করার ফাংশন
def is_subscribed(user_id):
    url = f"https://www.googleapis.com/youtube/v3/subscriptions?part=id&forChannelId={CHANNEL_ID}&mine=true&key={YOUTUBE_API_KEY}"
    headers = {"Authorization": f"Bearer {user_id}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False

# ফেক স্ক্রিনশট তৈরির ফাংশন
def create_fake_screenshot(phone_number, amount, template_type='bkash', name=None):
    if template_type == 'bkash':
        img = Image.open('bkash_template.png')  # Bkash টেমপ্লেট লোড
        phone_number_position = (279, 638)
        amount_position = (127, 1094)
        transaction_id_position = (600, 905)
        full_time_date_position = (90.7, 898)
        name_position = (279, 590)  # বিকাশের ক্ষেত্রে নামের জন্য পজিশন
        current_time_position = (29, 18)

    else:
        img = Image.open('nagad_template.png')  # Nagad টেমপ্লেট লোড
        phone_number_position = (400, 580)
        amount_position = (830, 860)
        amount_plus_five_position = (830, 1000)
        transaction_id_position = (820, 770)
        full_time_date_position = (650, 1070)
        current_time_position = (44, 17)

    draw = ImageDraw.Draw(img)

    # "Allrounder Grotesk" ফন্ট লোড করা
    font = ImageFont.truetype('arialbd.ttf', 40)

    # বর্তমান সময় এবং তারিখ নেওয়া
    current_time = datetime.now().strftime('%I:%M %p')
    current_date = datetime.now().strftime('%d/%m/%Y')
    full_time_date = f'{current_time} {current_date}'

    # টাকার পরিমাণ + ৫
    amount_plus_five = int(amount) + 5

    # র্যান্ডম ট্রানজেকশন আইডি তৈরি
    transaction_id = generate_transaction_id()

    # সঠিক জায়গায় টেক্সট বসানো
    draw.text(phone_number_position, f'{phone_number}', font=font, fill='#727272')
    draw.text(current_time_position, f'{current_time}', font=font, fill='white')
    draw.text(amount_position, f'{amount}', font=font, fill='#727272')

    # নগদের জন্য amount_plus_five যোগ করা
    if template_type == 'nagad':
        draw.text(amount_plus_five_position, f'{amount_plus_five}', font=font, fill='#727272')
    
    draw.text(transaction_id_position, f'{transaction_id}', font=font, fill='#727272')
    draw.text(full_time_date_position, f'{full_time_date}', font=font, fill='#727272')

    # যদি বিকাশ হয় তবে নাম যোগ করা হবে
    if template_type == 'bkash' and name:
        draw.text(name_position, f'{name}', font=font, fill='#727272')

    # ফেক স্ক্রিনশট সেভ করা
    img.save('fake_screenshot.png')

# নতুন ব্যবহারকারীকে ওয়েলকাম মেসেজ এবং সাবস্ক্রিপশন চেক মেসেজ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "স্বাগতম! আমাদের ইউটিউব চ্যানেলে সাবস্ক্রাইব করুন এবং তারপর স্ক্রিনশট তৈরি করতে পারেন।")
    bot.send_message(message.chat.id, "আপনার সাবস্ক্রিপশন স্ট্যাটাস চেক করার জন্য /check_subscription ব্যবহার করুন।")

# সাবস্ক্রিপশন চেক করার কমান্ড
@bot.message_handler(commands=['check_subscription'])
def check_subscription(message):
    user_id = message.from_user.id

    if is_subscribed(user_id):
        bot.send_message(message.chat.id, "আপনার সাবস্ক্রিপশন নিশ্চিত করা হয়েছে! এখন আপনি বটটি ব্যবহার করতে পারেন।")
        show_menu(message.chat.id)  # ব্যবহারকারীর জন্য মেনু দেখানো
    else:
        bot.send_message(message.chat.id, "দয়া করে আমাদের ইউটিউব চ্যানেলে সাবস্ক্রাইব করুন এবং আবার চেষ্টা করুন।")

# মেনু প্রদর্শনের জন্য একটি ফাংশন
def show_menu(chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Nagad Screenshot', callback_data='nagad'))
    markup.add(telebot.types.InlineKeyboardButton('Bkash Screenshot', callback_data='bkash'))
    bot.send_message(chat_id, "একটি অপশন বেছে নিন:", reply_markup=markup)

# ইনলাইন বোতামের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data in ['nagad', 'bkash'])
def handle_menu(call):
    user_data[call.message.chat.id] = {'template_type': call.data}
    
    # ইউজারকে নম্বর দিতে বলা
    bot.send_message(call.message.chat.id, "আপনার ১১ ডিজিটের নম্বর লিখুন : ১/৩")
    bot.register_next_step_handler(call.message, get_phone_number)

# ইউজারের ফোন নম্বর নেওয়া
def get_phone_number(message):
    phone_number = message.text

    if len(phone_number) == 11 and phone_number.isdigit():
        user_data[message.chat.id]['phone_number'] = phone_number
        
        if user_data[message.chat.id]['template_type'] == 'bkash':
            bot.send_message(message.chat.id, "আপনার নাম লিখুন : ২/৩")
            bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.chat.id, "এখন আপনার টাকার পরিমান লিখুন : ২/২")
            bot.register_next_step_handler(message, get_amount)
    else:
        bot.send_message(message.chat.id, "ভুল নাম্বার! দয়া করে সঠিক ১১ ডিজিটের ফোন নম্বর দিন।")
        bot.register_next_step_handler(message, get_phone_number)

# বিকাশের ক্ষেত্রে নাম নেওয়া
def get_name(message):
    name = message.text
    user_data[message.chat.id]['name'] = name
    bot.send_message(message.chat.id, "এখন আপনার টাকার পরিমান লিখুন : ৩/৩")
    bot.register_next_step_handler(message, get_amount)

# ইউজারের কাছ থেকে টাকার পরিমাণ নেওয়া
def get_amount(message):
    amount = message.text

    if amount.isdigit():
        user_data[message.chat.id]['amount'] = amount

        phone_number = user_data[message.chat.id]['phone_number']
        template_type = user_data[message.chat.id]['template_type']
        name = user_data[message.chat.id].get('name')

        create_fake_screenshot(phone_number, amount, template_type, name)

        with open('fake_screenshot.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        bot.send_message(message.chat.id, "আপনি যদি আবার স্ক্রিনশট তৈরি করতে চান, মেনু থেকে একটি অপশন বেছে নিন:")
        show_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "ভুল ইনপুট! দয়া করে শুধুমাত্র সংখ্যায় টাকার পরিমাণ লিখুন।")
        bot.register_next_step_handler(message, get_amount)

# বট চালু
bot.polling()
