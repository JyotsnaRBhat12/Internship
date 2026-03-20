from flask import Flask, request, jsonify
from models import db, User, Note, TokenBlocklist, Category, Tag
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
    inspector = inspect(db.engine)

    if not inspector.has_table("user"):
        return

    user_columns = {column["name"] for column in inspector.get_columns("user")}

    if "password_hash" not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN password_hash VARCHAR(255)"))

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


# ---------------- USER AUTH ---------------- #

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 409

    hashed_password = generate_password_hash(password)

    user = User(
        username=username,
        password=hashed_password,
        password_hash=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    })


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]

    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()

    return jsonify({"message": "Logout successful"})


# ---------------- CATEGORY API ---------------- #

@app.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    data = request.get_json()
    name = data.get("name")

    category = Category(name=name)

    db.session.add(category)
    db.session.commit()

    return jsonify({"message": "Category created", "id": category.id})


@app.route("/categories", methods=["GET"])
@jwt_required()
def get_categories():
    categories = Category.query.all()

    result = [{"id": c.id, "name": c.name} for c in categories]

    return jsonify({"categories": result})


# ---------------- TAG API ---------------- #

@app.route("/tags", methods=["POST"])
@jwt_required()
def create_tag():
    data = request.get_json()
    name = data.get("name")

    tag = Tag(name=name)

    db.session.add(tag)
    db.session.commit()

    return jsonify({"message": "Tag created", "id": tag.id})


@app.route("/tags", methods=["GET"])
@jwt_required()
def get_tags():
    tags = Tag.query.all()

    result = [{"id": t.id, "name": t.name} for t in tags]

    return jsonify({"tags": result})


# ---------------- NOTES CRUD ---------------- #

@app.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())

    data = request.get_json()
    content = data.get("content")
    category_id = data.get("category_id")
    tag_ids = data.get("tags", [])

    note = Note(content=content, user_id=user_id)

    if category_id:
        note.category_id = category_id

    if tag_ids:
        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        note.tags = tags

    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Note created", "note_id": note.id})


@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())

    category = request.args.get("category")
    tag = request.args.get("tag")
    search = request.args.get("search")

    query = Note.query.filter_by(user_id=user_id)

    if category:
        query = query.join(Category).filter(Category.name == category)

    if tag:
        query = query.join(Note.tags).filter(Tag.name == tag)

    if search:
        query = query.filter(Note.content.ilike(f"%{search}%"))

    notes = query.all()

    result = []

    for note in notes:
        result.append({
            "id": note.id,
            "content": note.content,
            "category": note.category.name if note.category else None,
            "tags": [t.name for t in note.tags]
        })

    return jsonify({"notes": result})


@app.route("/notes/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id):
    user_id = int(get_jwt_identity())

    data = request.get_json()
    content = data.get("content")

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    note.content = content
    db.session.commit()

    return jsonify({"message": "Note updated"})


@app.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    user_id = int(get_jwt_identity())

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Note deleted"})


if __name__ == "__main__":
    app.run(debug=True)