"""
User command handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.user_service import user_service
from app.services.ai_models import ai_model_service
from app.core.redis_client import redis_client


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name or "Unknown"
    
    # Get or create user
    async for session in get_db_session():
        await user_service.get_or_create_user(session, user_id, username, first_name)
    
    welcome_text = f"""
🤖 **Welcome to AI Bot, {first_name}!**

I'm your intelligent assistant powered by multiple AI models. Here's what you can do:

**Commands:**
/start - Show this welcome message
/setmodel - Choose your preferred AI model
/setkey - Set your custom API key
/clear - Clear conversation history
/help - Show help information

**Features:**
• Chat with various AI models (GPT-4, Claude, Gemini)
• Use your own API keys for unlimited usage
• Group chat support with authorization
• Conversation context management

Just send me a message to start chatting! 🚀
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def setmodel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setmodel command"""
    user_id = update.effective_user.id
    
    # Get available models
    async for session in get_db_session():
        models = await ai_model_service.get_available_models(session)
    
    if not models:
        await update.message.reply_text("❌ No AI models are currently available.")
        return
    
    # Create inline keyboard
    keyboard = []
    for model in models:
        button_text = f"{model.model_name} ({model.api_provider})"
        callback_data = f"setmodel_{model.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **Choose your preferred AI model:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def setmodel_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setmodel callback query"""
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("setmodel_"):
        return
    
    model_id = int(query.data.split("_")[1])
    user_id = update.effective_user.id
    
    # Set user's model
    async for session in get_db_session():
        success = await user_service.set_user_model(session, user_id, model_id)
    
    if success:
        # Get model name for confirmation
        async for session in get_db_session():
            model = await ai_model_service.get_model_config(session, model_id)
        
        if model:
            await query.edit_message_text(
                f"✅ **Model set successfully!**\n\n"
                f"Selected: {model.model_name} ({model.api_provider})\n\n"
                f"You can now start chatting with this AI model!",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("✅ Model set successfully!")
    else:
        await query.edit_message_text("❌ Failed to set model. Please try again.")


async def setkey_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setkey command"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "🔑 **Set your API key:**\n\n"
            "Usage: `/setkey <model_id> <api_key>`\n\n"
            "First, use `/setmodel` to see available models and their IDs.",
            parse_mode='Markdown'
        )
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /setkey <model_id> <api_key>")
        return
    
    try:
        model_id = int(context.args[0])
        api_key = context.args[1]
    except ValueError:
        await update.message.reply_text("❌ Invalid model ID.")
        return
    
    # Verify model exists
    async for session in get_db_session():
        model = await ai_model_service.get_model_config(session, model_id)
    
    if not model:
        await update.message.reply_text("❌ Invalid model ID.")
        return
    
    # Set API key
    async for session in get_db_session():
        success = await user_service.set_user_api_key(session, user_id, model_id, api_key)
    
    if success:
        await update.message.reply_text(
            f"✅ **API key set successfully!**\n\n"
            f"Model: {model.model_name} ({model.api_provider})\n"
            f"Your custom API key is now configured for this model.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to set API key. Please try again.")


async def clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear command"""
    user_id = update.effective_user.id
    
    # Clear user context
    await user_service.clear_user_context(user_id)
    
    await update.message.reply_text(
        "🧹 **对话历史已清除！**\n\n"
        "你的聊天上下文已重置，现在可以开始新的对话了。",
        parse_mode='Markdown'
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
🤖 **AI Bot Help**

**Commands:**
/start - Welcome message and bot introduction
/setmodel - Choose your preferred AI model
/setkey - Set your custom API key for a model
/clear - Clear your conversation history
/help - Show this help message

**How to use:**
1. Use `/setmodel` to choose an AI model
2. Optionally use `/setkey` to set your own API key
3. Just send me a message to start chatting!

**Features:**
• Multiple AI models (GPT-4, Claude, Gemini)
• Custom API key support
• Group chat with authorization
• Conversation context management
• Rate limiting for fair usage

**Need help?** Contact an administrator if you have issues.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
