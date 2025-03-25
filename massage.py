# Messages used by the bot

WELCOME_MESSAGE = """
👋 Salom <b>{user_name}</b>!

Bizning maxfiy guruhga kirish uchun siz <b>5 ta odamni</b> taklif qilishingiz kerak.

⚠️ Muhim: Siz VA taklif qilgan odamlaringiz <b>@kimyo_ess</b> va <b>@kimyo_ess_video_yechimlari</b> kanallariga a'zo bo'lishingiz shart!

🔗 Sizning takliflar havolangiz:
<code>{referral_link}</code>

Hozirgi taklif qilganlaringiz: <b>{current_invites}/{required_invites}</b>

5 ta odam sizning havolangiz orqali botga qo'shilganidan so'ng, sizga maxfiy guruhga kirish havolasi yuboriladi!
"""

HELP_MESSAGE = """
🔹 <b>Bot qanday ishlaydi:</b>

1. <b>@kimyo_ess</b> va <b>@kimyo_ess_video_yechimlari</b> kanallariga a'zo bo'ling!

2. Quyidagi havolani do'stlaringizga yuboring:
<code>{referral_link}</code>

3. Do'stlaringiz havola orqali botga kirgandan so'ng, ular ham kanallarimizga a'zo bo'lishi kerak. Shunda ular sizning taklifingiz hisoblanadi.

4. <b>{required_invites} ta odam</b> taklif qilganingizdan so'ng, siz maxfiy guruhga a'zo bo'lasiz!

5. Taklif qilgan odamlaringiz sonini tekshirish uchun /check buyrug'ini yuboring.

Omad! 🍀
"""

ALREADY_JOINED_MESSAGE = """
Siz allaqachon botdan foydalanyapsiz! Boshqalarni taklif qilish uchun quyidagi havoladan foydalaning:

<code>{referral_link}</code>
"""

REFERRAL_LINK_MESSAGE = """
🔗 Sizning taklif havolangiz:

<code>{referral_link}</code>

Bu havolani do'stlaringizga yuboring. Botga <b>{required_invites} ta odam</b> qo'shilganda, siz maxfiy guruhga kirish huquqini olasiz!
"""

REWARD_MESSAGE = """
🎉 <b>Tabriklaymiz!</b>

Siz muvaffaqiyatli tarzda <b>5 ta odamni</b> taklif qildingiz va maxfiy guruhga kirish huquqini qo'lga kiritdingiz!

🔐 Maxfiy guruhga kirish havolasi:
<a href="{secret_group_link}">Maxfiy guruhga kirish</a>

Bu havolani boshqalar bilan ulashmang!
"""

INVITES_PROGRESS_MESSAGE = """
📊 <b>Sizning taklif statistikangiz:</b>

✅ Hozirgi takliflar: <b>{current_invites}/{required_invites}</b>
⏳ Qolgan takliflar: <b>{remaining_invites}</b>

⚠️ Eslatma: Takliflar sanalishi uchun siz va do'stlaringiz <b>@kimyo_ess</b> va <b>@kimyo_ess_video_yechimlari</b> kanallariga a'zo bo'lishingiz shart!

🔗 <b>Taklif havolangiz:</b>
<code>{referral_link}</code>

Bu havolani do'stlaringizga yuboring va maxfiy guruhga kirish huquqini qo'lga kiriting!
"""
