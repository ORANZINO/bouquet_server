from app.database.schema import UserBlocks, CharacterBlocks, Characters
from sqlalchemy import or_

def block_characters(user, session):
    user_blocks = session.query(UserBlocks).filter(or_(UserBlocks.user_id == user['id'], UserBlocks.blocked_id == user['id'])).all()
    block_users = []
    for block in user_blocks:
        if block.user_id == user['id']:
            block_users.append(block.blocked_id)
        else:
            block_users.append(block.user_id)
    character_blocks = session.query(CharacterBlocks).filter(or_(CharacterBlocks.character_id == user['default_character_id'], CharacterBlocks.blocked_id == user['default_character_id'])).all()
    block_characters = session.query(Characters.id).filter(Characters.user_id.in_(block_users)).all()
    block_characters = [character[0] for character in block_characters]
    for block in character_blocks:
        if block.character_id == user['default_character_id']:
            block_characters.append(block.blocked_id)
        else:
            block_characters.append(block.character_id)
    return block_characters
