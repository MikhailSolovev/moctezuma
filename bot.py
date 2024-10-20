from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton, CallbackQuery,
)
import random
import string
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime, timedelta
from aiogram.dispatcher import FSMContext
from requests import SubsClient, PaymentClient
import asyncio


# Создаем объект бота
b = Bot(token="7975681129:AAFFHWejLU-_ZneMCMET9TGqVgJTFsvHQdM", parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(b, storage=storage)

BALANCE_EURO = 8329.45
BALANCE_DIGITAL = 428.47
BALANCE_TOKEN = 4
main_account_id = "351012345674"


class StateMember(StatesGroup):
    not_registered = State()
    registered = State()


class State_Manager(StatesGroup):
    get_addres = State()
    get_amount = State()
    confirm = State()

class State_Manager_digit(StatesGroup):
    get_addres = State()
    get_amount = State()
    confirm = State()

def generate_past_datetime_today():
    now = datetime.now()
    start_of_day = datetime.combine(now.date(), datetime.min.time())
    seconds_since_start_of_day = (now - start_of_day).total_seconds()
    if seconds_since_start_of_day <= 0:
        raise ValueError("День только начался, нет прошедшего времени для генерации.")
    random_past_seconds = random.uniform(0, seconds_since_start_of_day)
    past_datetime = start_of_day + timedelta(seconds=random_past_seconds)

    return past_datetime


def gen_hash() -> str:
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(40)
    )

@dp.message_handler(commands=["start"])
async def transactions(message: types.Message, state: FSMContext):
    await b.send_message(
        message.chat.id,
        "<b>Welcome to Moctezuma!</b>",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
        .add(KeyboardButton('👤 Profile'))

    )
    await b.send_message(
        message.chat.id,
        'Register with Bank of Cyprus',
        reply_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Register by BoC", url=await SubsClient().create_subscription())
            )
        )

    await asyncio.sleep(20)
    await b.send_message(message.chat.id, '<b>Thank you for registration!</b>')
    await profile(message)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith("history"))
async def transactions(callback: CallbackQuery):
    try:
        await b.send_message(
            callback.message.chat.id,
            "<b>Digit-€ Transactions:</b>",
            reply_markup=create_tran_keyboard(),
        )
    except Exception as e:
        print(e)


@dp.message_handler(text="👤 Profile")
async def profile(message: types.Message):
    """API Solana"""
    url = "solana"
    text = f"<b>• BoC Balance:</b>  <code>{BALANCE_EURO}</code>€\n<b>• Digit-EUR:</b>•  <code>{BALANCE_DIGITAL}</code>€\n<b>• Assets:</b>   <code>{BALANCE_TOKEN}</code>"
    await b.send_message(
        message.chat.id,
        f"Profile: <i>{message.from_user.first_name}</i>\nRegistrated: <code>20.10.2024</code>\nCurrency: <b>EUR</b>\n\n{text}",
        reply_markup=InlineKeyboardMarkup()
        .add(InlineKeyboardButton('💠 Transfer Dig-EUR', callback_data='tran_dig'))
        .insert(InlineKeyboardButton('💶 Transfer EUR', callback_data='tran_eur'))
        .add(InlineKeyboardButton('📁 Balance history ', callback_data='history'))
        .add(InlineKeyboardButton('🏛 Tokenize assets', callback_data='tokenize'))
    )


############################ EUR PAYMENTS ############################
@dp.callback_query_handler(lambda x: x.data and x.data.startswith("tran_eur"))
async def transfer_eur(callback: CallbackQuery):
    await callback.message.answer(f"Send an <b>account ID</b> of receiver")
    await State_Manager.get_addres.set()


@dp.message_handler(state=State_Manager.get_addres)
async def get_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message.text
    await message.answer("Send an <b>amount in EUR</b>")
    await State_Manager.get_amount.set()


@dp.message_handler(state=State_Manager.get_amount)
async def get_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["amount"] = message.text
        await message.answer(
            f'❔ Are you sure that you want to send <b>{data["amount"]}</b> EUR to BoC user, with <b>account ID</b>: <code>{data["address"]}</code>?',
            reply_markup=InlineKeyboardMarkup()
            .add(InlineKeyboardButton(
                'Yes, confirm payment',
                url=await PaymentClient().create_payment(amount=float(data["amount"]), debtor_id=main_account_id,
                                                         creditor_id=data["address"]))
            )
            .add(InlineKeyboardButton('No, cancel', callback_data='clear'))
        )
        await asyncio.sleep(23)
        await message.answer(
            f'✔️ <b>{data["amount"]}</b> has successfully sent to account ID <code>{data["address"]}</code>\nTrans. hash: <code>{gen_hash()}\n\n</code><i>You can view a transaction details in the transaction history</i>'
        )
        await asyncio.sleep(2)
        await profile(message)
        await state.finish()

@dp.message_handler(state="*")
async def confirm_transfer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(
            f'✔️ <b>{data["amount"]}</b> has successfully sent to account ID <code>{data["address"]}</code>\nTrans. hash: <code>{gen_hash()}\n\n</code><i>You can view a transaction details in the transaction history</i>'
        )
    await profile(message)
    await state.finish()


############################ DIGITAL PAYMENTS ############################
@dp.callback_query_handler(lambda x: x.data and x.data.startswith("tran_dig"))
async def transfer_eur_digit(callback: CallbackQuery):
    await callback.message.answer(f"Send an <b>account ID</b> of receiver")
    await State_Manager_digit.get_addres.set()


@dp.message_handler(state=State_Manager_digit.get_addres)
async def get_address_digit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message.text
    await message.answer("Send an <b>amount in EUR</b>")
    await State_Manager_digit.get_amount.set()




@dp.message_handler(state=State_Manager_digit.get_amount)
async def get_amount_digit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["amount"] = message.text
        await message.answer(
            f'❔ Are you sure that you want to send <b>{data["amount"]}</b> EUR to BoC user, with <b>account ID</b>: <code>{data["address"]}</code>?',
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Yes, confirm payment')).add(
                KeyboardButton('No, cancel'))
        )
        await State_Manager_digit.confirm.set()


@dp.message_handler(state=State_Manager_digit.confirm)
async def confirm_transfer_digit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Yes, confirm payment":
            await message.answer(
                f'✔️ <b>{data["amount"]}</b> has successfully sent to account ID <code>{data["address"]}</code>\n\nTrans. hash: <code>{gen_hash()}\n\n</code><i>You can view a transaction details in the transaction history</i>'
            )
        else:
            await message.answer("Canceled")
    await state.finish()
########################################################


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("n_fake"))
async def n_fake_callback(callback: types.CallbackQuery):
    parts_callback = callback.data.split("_")
    action = parts_callback[-2]
    value = parts_callback[-1]
    if action == "id":
        amount_random = float(parts_callback[-4])
        hash_random = parts_callback[-3]
        status_random = parts_callback[-5]
        text = f"<b>Date:</b> <code>{generate_past_datetime_today()}</code>\n<b>Amount:</b> {amount_random}\n<b>Charges:</b> <code>{amount_random*0.01}</code>\n<b>Currency: </b>EUR\n<b>Hash:</b> <code>{hash_random}</code>\n\n<b>Status:</b> {status_random}"

        await callback.message.reply(
            text,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="Clear", callback_data="clear")
            ),
        )


@dp.callback_query_handler(lambda x: x.data and x.data.startswith("clear"), state='*')
async def clear_callback(callback: types.CallbackQuery, state: FSMContext):
    await b.delete_message(callback.message.chat.id, callback.message.message_id)
    await state.finish()


def create_tran_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=4)
    statuses: list = ["🟢", "🟢", "🔺"]
    keyboard.add(InlineKeyboardButton("ID:", callback_data="n"))
    keyboard.insert(InlineKeyboardButton("Amount:", callback_data="n"))
    keyboard.insert(InlineKeyboardButton("Hash:", callback_data="n"))
    keyboard.insert(InlineKeyboardButton("Status:", callback_data="n"))
    amount_random = round(random.uniform(10.0, 100.0), 2)
    status_random = random.choice(statuses)
    hash_random = str(gen_hash())
    keyboard.add(
        InlineKeyboardButton(
            "#1",
            callback_data=f"n_fake_{status_random}_{amount_random}_{hash_random}_id_1",
        )
    )
    keyboard.insert(
        InlineKeyboardButton(
            f"{amount_random}€", callback_data=f"n_fake_amount_{amount_random}"
        )
    )

    keyboard.insert(
        InlineKeyboardButton(hash_random, callback_data=f"n_fake_hash_{hash_random}")
    )
    keyboard.insert(
        InlineKeyboardButton(
            str(status_random), callback_data=f"n_fake_status_{str(status_random)}"
        )
    )

    for _ in range(1, 10):
        amount_random = round(random.uniform(10.0, 100.0), 2)
        status_random = random.choice(statuses)
        hash_random = str(gen_hash())
        num = InlineKeyboardButton(
            f"#{_ + 1}",
            callback_data=f"n_fake_{status_random}_{amount_random}_{hash_random}_id_{_}",
        )
        amount = InlineKeyboardButton(
            f"{amount_random}€", callback_data=f"n_fake_amount_{amount_random}"
        )

        hash = InlineKeyboardButton(
            hash_random, callback_data=f"n_fake_hash_{hash_random}"
        )
        status = InlineKeyboardButton(
            str(status_random), callback_data=f"n_fake_status_{str(status_random)}"
        )

        keyboard.add(num).insert(amount).insert(hash).insert(status)

    keyboard.add(InlineKeyboardButton("·1·", callback_data="1")).insert(
        InlineKeyboardButton("2", callback_data="1")
    ).insert(InlineKeyboardButton("2", callback_data="1"))

    return keyboard





# Запускаем бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
