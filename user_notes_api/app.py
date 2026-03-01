from flask import Flask, request, jsonify
from models import db, User, Note, TokenBlocklist
from config import Config
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)


def run_schema_migrations():
    """Lightweight migration for legacy local SQLite schema."""
    inspector = inspect(db.engine)

    if not inspector.has_table("user"):
        return

    user_columns = {column["name"] for column in inspector.get_columns("user")}

    if "password_hash" not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN password_hash VARCHAR(255)"))

    if "password" in user_columns:
        legacy_rows = db.session.execute(text("SELECT id, password, password_hash FROM user")).all()
        for row in legacy_rows:
            if row.password_hash:
                continue
            if row.password:
                hashed = generate_password_hash(row.password)
                db.session.execute(
                    text(
                        "UPDATE user SET password_hash = :password_hash, password = :password WHERE id = :id"
                    ),
                    {
                        "password_hash": hashed,
                        "password": hashed,
                        "id": row.id,
                    },
                )

    db.session.commit()


with app.app_context():
    db.create_all()
    run_schema_migrations()


@jwt.token_in_blocklist_loader
def is_token_revoked(_jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None


@app.route("/")
def home():
    return jsonify({"message": "User Notes API Running"}), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    stored_hash = user.password_hash if user and user.password_hash else (user.password if user else None)

    if not user or not stored_hash or not check_password_hash(stored_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.password_hash:
        user.password_hash = stored_hash
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return jsonify({"message": "Login successful", "access_token": access_token}), 200


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify({"message": "Logout successful"}), 200


@app.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    content = data.get("content")

    if not content:
        return jsonify({"error": "content is required"}), 400

    note = Note(content=content, user_id=user_id)
    db.session.add(note)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Note created successfully",
                "note": {"id": note.id, "content": note.content},
            }
        ),
        201,
    )


@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())
    notes = Note.query.filter_by(user_id=user_id).all()

    result = [{"id": note.id, "content": note.content} for note in notes]

    return jsonify({"notes": result}), 200


@app.route("/notes/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    content = data.get("content")

    if not content:
        return jsonify({"error": "content is required"}), 400

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    note.content = content
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Note updated successfully",
                "note": {"id": note.id, "content": note.content},
            }
        ),
        200,
    )


@app.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    user_id = int(get_jwt_identity())

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Note deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
