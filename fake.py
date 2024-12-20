import telebot
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import string
import os  # ফাইল ডিলিট করার জন্য os মডিউল আমদানি করা

# বটের টোকেন এবং গ্রুপ আইডি
bot = telebot.TeleBot('7768232321:AAEIxiScxQfadADzTGzicsyJ56oDxhfkl1U')
GROUP_ID = -1002261392190  # আপনার গ্রুপের আইডি এখানে দিন

# ইনপুট সংরক্ষণের জন্য একটি dictionary ব্যবহার করা হবে
user_data = {}

# ৮ অক্ষরের র্যান্ডম ট্রানজেকশন আইডি তৈরি ফাংশন
def generate_transaction_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ইউজারের গ্রুপে যুক্ত থাকা চেক করার ফাংশন
def is_member(user_id):
    try:
        member = bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ['member', 'administrator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# ফেক স্ক্রিনশট তৈরির ফাংশন
def create_fake_screenshot(phone_number, amount, template_type='bkash', name=None):
    if template_type == 'bkash':
        img = Image.open('bkash_template.png')  # Bkash টেমপ্লেট লোড
        phone_number_position = (279, 638)
        amount_position = (127, 1094)
        transaction_id_position = (600, 905)
        full_time_date_position = (90, 898)
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

    # রেন্ডম ফাইল নাম তৈরি করা
    file_name = f"fake_screenshot_{generate_transaction_id()}.png"
    
    # স্ক্রিনশট সেভ করা
    img.save(file_name)
    return file_name

# নতুন ব্যবহারকারীকে ওয়েলকাম মেসেজ এবং গ্রুপে যুক্ত হওয়ার মেসেজ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "স্বাগতম! আমাদের Telegram গ্রুপে যুক্ত হন এবং তারপর স্ক্রিনশট তৈরি করতে পারেন।")
    bot.send_message(message.chat.id, "গ্রুপে যুক্ত হতে এখানে ক্লিক করুন: https://t.me/+VKifhnq-QbFhYTI1")
    bot.send_message(message.chat.id, "গ্রুপে যুক্ত হওয়ার পর /check_membership ব্যবহার করুন।")

# সদস্যপদ চেক করার কমান্ড
@bot.message_handler(commands=['check_membership'])
def check_membership(message):
    user_id = message.from_user.id

    if is_member(user_id):
        bot.send_message(message.chat.id, "আপনার সদস্যপদ নিশ্চিত করা হয়েছে! এখন আপনি বটটি ব্যবহার করতে পারেন।")
        show_menu(message.chat.id)  # ব্যবহারকারীর জন্য মেনু দেখানো
    else:
        bot.send_message(message.chat.id, "দয়া করে আমাদের Telegram গ্রুপে যুক্ত হন এবং আবার চেষ্টা করুন।")

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

        # ফেক স্ক্রিনশট তৈরি এবং ফাইল নাম পাওয়া
        file_name = create_fake_screenshot(phone_number, amount, template_type, name)

        # ফাইল পাঠানো
        with open(file_name, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        # কিছুক্ষণ পর ফাইল ডিলিট করা
        os.remove(file_name)

        bot.send_message(message.chat.id, "আপনি যদি আবার স্ক্রিনশট তৈরি করতে চান, মেনু থেকে একটি অপশন বেছে নিন:")
        show_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "ভুল ইনপুট! দয়া করে শুধুমাত্র সংখ্যায় টাকার পরিমাণ লিখুন।")
        bot.register_next_step_handler(message, get_amount)

# বট চালু
bot.polling()
