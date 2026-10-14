from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify
import json


def ai_interaction(ai_service):
    bp = Blueprint("ai", __name__)

    @bp.route("/", methods=["GET", "POST"])
    def list_models():
        if request.method == "POST":
            model = request.form.get("model")
            if model:
                ai_service.model_select(model)

        models = ai_service.query_available_lm()
        return render_template(
            "aichat.html", models=models, selected_model=ai_service.model_selected or None,
        )

    @bp.route("/chat", methods=["POST"])
    def ask_ai():
        history_raw = request.form.get("history", "[]")
        user_message = request.form.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "No message provided."}), 400

        if not ai_service.model_selected:
            return jsonify({"error": "No model selected. Load a model first."}), 400

        try:
            conversation_history = json.loads(history_raw)
        except (json.JSONDecodeError, TypeError):
            conversation_history = []

        ai_response = ai_service.chat_with_lm_studio(user_message, conversation_history)
        return jsonify({"response": ai_response})

    @bp.route("/lmstudioIP", methods=["POST"])
    def updateIP():
        return True

    @bp.route("/downloadmodel", methods=["POST"])
    def downloadModel():
        return True

    return bp