from bot.handlers.hr.services import UserService
from bot.handlers.balance.keyboards import balance_kb
from bot.handlers.callback_datas import MenuCallback

from aiogram import F, Router
from aiogram import types
from aiogram.enums import ParseMode


router = Router()

@router.message(F.text == "баланс")
async def get_user_balance(message: types.Message):
    free_tokens, paid_tokens = await UserService.get_balance(
        user_id=message.from_user.id
    )
    if free_tokens < 0:
        free_tokens = 0

    reply_text = "Баланс:\n" + \
        f"Обычных токенов {free_tokens:,}\n" + \
        f"Платных токенов {paid_tokens:,}\n" + \
        f"Итого токенов {free_tokens+paid_tokens:,}\n" + \
        "\n Способы пополнения баланса:\n" + \
        "- Пригласить друга по реферальной программе" + \
        "\n(Нажми чуть ниже кнопку <b>Реферальная ссылка</b>)\n" + \
        "- Купить токены (Этот способ в разработке, скоро появится!)"
    await message.answer(
        text=reply_text, reply_markup=balance_kb, parse_mode=ParseMode.HTML
    )

@router.callback_query(MenuCallback.filter(
        (F.handler == 'balance') & (F.level == '1')
    ))
async def show_ref(callback: types.CallbackQuery, callback_data: MenuCallback):
    print(callback_data)
    user_id = callback.from_user.id
    referral_link = UserService.encode_user_id(user_id)
    referral_count = await UserService.get_referral_count(user_id)
    reply_text = "Ваша реферальная ссылка (скопируйте и отправьте её другу):\n\n" + \
    referral_link + \
    f"\nВы пригласили {referral_count} друзей\n\n" + \
    "Поделитесь ссылкой со своим другом и получите 100 000 платных токенов за каждого активного участника. Приглашённый пользователь должен сделать не менее 3-х запросов, после чего вам начислятся токены." 
    await callback.message.answer(text=reply_text)
    await callback.answer()
    

