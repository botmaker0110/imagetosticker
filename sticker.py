import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
from PIL import Image

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Replace 'YOUR_API_TOKEN' with your actual bot API token
TOKEN = '7975152935:AAGuVM7AA_JuThtaWKEbEvHyT1Jomn6BKmU'

# Initialize the Application
application = Application.builder().token(TOKEN).build()

# Loading sticker ID (replace this with your actual sticker ID)
loading_sticker_id = 'CAACAgEAAxkBAAIBJWe4KbyGnCvYtqGVYKIIjcWJYKu8AAIDAwAC54zYRtJM1QZbUVMyNgQ'  # Replace with your sticker file ID

# File to store user IDs
USER_IDS_FILE = 'user_ids.txt'

# Function to handle received images and convert them to stickers
async def handle_image(update: Update, context: CallbackContext) -> None:
    # Send the typing action first
    await update.message.reply_text("Processing... Please wait.")
    await update.message.chat.send_action(action="typing")  # Show typing action
    
    # Send the loading sticker
    loading_msg = await update.message.reply_sticker(loading_sticker_id)
    
    # Get the image file sent by the user (in the highest resolution)
    file = await update.message.photo[-1].get_file()  # Get the highest quality photo
    
    # Temporary path to store the downloaded image
    image_path = 'image.jpg'  # You can change this to any temporary path
    await file.download_to_drive(image_path)  # Download the image file
    
    # Convert the image to .webp format (use Pillow to open and save as .webp)
    try:
        # Open the image with Pillow
        img = Image.open(image_path)
        
        # Convert the image to webp (you can adjust this to fit your needs)
        sticker_path = 'sticker.webp'  # Path to save the sticker
        
        # Save the image as .webp with transparency (if needed)
        img.convert("RGBA").save(sticker_path, 'WEBP')

        # Delete the loading sticker once processing is complete
        await loading_msg.delete()

        # Send the converted sticker
        await update.message.reply_sticker(sticker=sticker_path)

        # Optionally, delete the temporary files after processing
        os.remove(image_path)  # Remove the original image
        os.remove(sticker_path)  # Remove the sticker image (optional, if not needed anymore)

    except Exception as e:
        # Handle errors (e.g., invalid image format)
        await update.message.reply_text(f"Error processing the image: {e}")

# Command handler to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    # Add user ID to the list
    user_id = update.message.from_user.id
    with open(USER_IDS_FILE, 'a') as f:
        f.write(f'{user_id}\n')

    # Define a better, more engaging image for the start message
    start_image_url = 'https://drive.google.com/uc?id=1iwDQPqnKnfH-BgAQyNhPkYHJAVs5h68V'  # Example of a more relevant image URL

    # Creating an inline keyboard with better visual design
    keyboard = [
        [InlineKeyboardButton("📖 How to Use", callback_data='how_to_use')],
        [InlineKeyboardButton("🚀 Get Started", callback_data='get_started')],
        [InlineKeyboardButton("🤔 FAQ", callback_data='faq')]  # An FAQ button for added value
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a sleek, polished welcome message
    await update.message.reply_photo(
        photo=start_image_url,
        caption=(
            "<b>Welcome to the Image to Sticker Bot!</b>\n\n"
            "🎨 Want to make your photos into cool stickers? You've come to the right place! 😎\n\n"
            "💡 Just send me an image, and I'll instantly turn it into a shiny sticker for you to share!\n\n"
            "🔹 <i>Use the buttons below to explore:</i>\n"
            "📖 Learn how to use me, 🚀 Get started, or 🤔 Check out the FAQ for more details.\n\n"
            "Let’s make stickers, shall we? 😁"
        ),
        parse_mode='HTML',  # This makes the caption bold, italics, and more visually structured.
        reply_markup=reply_markup
    )

# Command to broadcast a message to all users
async def broadcast(update: Update, context: CallbackContext) -> None:
    # Only allow the admin to broadcast
    admin_user_id = 6216990986  # Replace with your admin user ID
    if update.message.from_user.id != admin_user_id:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Get the message to broadcast from the command argument
    broadcast_message = ' '.join(context.args)
    
    if not broadcast_message:
        await update.message.reply_text("Please provide a message to broadcast.")
        return

    # Read user IDs from the file and send the message to each user
    with open(USER_IDS_FILE, 'r') as f:
        user_ids = [line.strip() for line in f.readlines()]

    success_count = 0
    failure_count = 0
    failed_users = []

    for user_id in user_ids:
        try:
            await context.bot.send_message(user_id, broadcast_message)
            success_count += 1  # Increment success counter
        except Exception as e:
            logging.error(f"Error sending message to {user_id}: {e}")
            failure_count += 1  # Increment failure counter
            failed_users.append(user_id)  # Add failed users to the list
    
    # Provide feedback to the admin
    await update.message.reply_text(
        f"Broadcast message sent to {success_count} users.\n"
        f"Failed to send to {failure_count} users. Check the logs for details."
    )

    # Optionally, log or handle failed users if needed
    if failure_count > 0:
        logging.error(f"Failed to send messages to the following users: {failed_users}")

# Callback function for inline button presses
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == 'how_to_use':
        # Send a new message with instructions on how to use the bot
        await query.message.reply_text(
            text="<b>How to Use:</b>\n\n"
                 "1. Send an image 📸 to the bot.\n"
                 "2. I will automatically convert your image into a sticker 🖼️.\n"
                 "3. Enjoy your cool new sticker and share it! 🎉\n\n"
                 "It's that easy! Just send an image, and I'll do the magic ✨",
            parse_mode='HTML'  # Keeping the same visual style
        )
    elif query.data == 'get_started':
        # Send a new message with information on getting started
        await query.message.reply_text(
            text="<b>Let's Get Started! 🚀</b>\n\n"
                 "Just send me an image, and I’ll convert it into a sticker in no time! ⏳\n\n"
                 "Let’s get creative! 🎨✨",
            parse_mode='HTML'  # Keeping the same style for consistency
        )
    elif query.data == 'faq':
        # Example: Add a FAQ section or other helpful information
        await query.message.reply_text(
            text="<b>❓ Frequently Asked Questions:</b>\n\n"
                 "1. <b>Can I send any image?</b> 🖼️\n"
                 "   - Yes, as long as it’s a supported image format (JPG, PNG, etc.)\n\n"
                 "2. <b>How long does it take to convert the image?</b> ⏳\n"
                 "   - It's super fast! You’ll receive your sticker instantly.\n\n"
                 "3. <b>What if my sticker isn't perfect?</b> 🤔\n"
                 "   - If you feel like the sticker needs adjustments, just let me know! 😁",
            parse_mode='HTML'  # Keeping the style consistent
        )

# Add handlers to the bot
start_handler = CommandHandler("start", start)
application.add_handler(start_handler)

# Add handler to process received images
image_handler = MessageHandler(filters.PHOTO, handle_image)
application.add_handler(image_handler)

# Add handler for broadcast command (admin only)
broadcast_handler = CommandHandler("broadcast", broadcast)
application.add_handler(broadcast_handler)

# Add callback query handler for inline buttons
application.add_handler(CallbackQueryHandler(button))

# Start polling
application.run_polling()
