from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost/recipes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Recipe(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return self.name

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class RecipeSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()


@app.route("/recipes")
def get_all_recipes():
    recipes = Recipe.get_all()

    serializer = RecipeSchema(many=True)

    data = serializer.dumps(recipes)

    return jsonify(data)


@app.route("/recipes", methods=["POST"])
def create_a_recipe():
    data = request.get_json()
    new_recipe = Recipe(
        name=data.get("name"),
        description=data.get("description"),
    )
    new_recipe.save()
    serializer = RecipeSchema()
    data = serializer.dumps(new_recipe)
    return jsonify(data), 201


@app.route("/recipe/<int:id>", methods=["GET"])
def get_recipes(id):
    recipe = Recipe.get_by_id(id)
    serializer = RecipeSchema()

    data = serializer.dumps(recipe)
    return jsonify(data), 200


@app.route("/recipe/<int:id>", methods=["PUT"])
def update_recipe(id):
    recipe_to_update = Recipe.get_by_id(id)
    data = request.get_json()
    recipe_to_update.name = data.get("name")
    recipe_to_update.description = data.get("description")

    db.session.commit()

    serializer = RecipeSchema()
    recipe_data=serializer.dumps(recipe_to_update)

    return jsonify(recipe_data), 200


@app.route("/recipes/<int:id>", methods=["DELETE"])
def delete_recipe(id):
    recipe_to_delete = Recipe.get_by_id(id)

    recipe_to_delete.delete()
    return jsonify({"message": "Deleted"}), 204


@app.errorhandler(500)
def internal_server(error):
    return jsonify({"message": "There is a problem"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Page not found"}), 404


@app.route('/')
def hello():
    return "Hello world"


if __name__ == "__main__":
    app.run(debug=True)
