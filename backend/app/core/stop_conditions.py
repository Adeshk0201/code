from app.config import CONFIDENCE_THRESHOLD

def should_stop(context):

    if context.state.question_count >= context.state.max_questions:
        return True

    if context.state.confidence >= CONFIDENCE_THRESHOLD:
        return True

    return False