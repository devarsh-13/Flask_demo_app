from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from models import User, Post

app = Flask(__name__)


driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))

# API route to create a user
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    new_user = User(username, email)

    with driver.session() as session:
        session.run("CREATE (u:User {username: $username, email: $email})", username=username, email=email)
        session.close()

    return jsonify({'message': 'User created successfully'}), 200

# API route to create a post and relate it to a user
@app.route('/post', methods=['POST'])
def create_post():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    new_post = Post(title, content,user_id)

    with driver.session() as session:
        session.run(
            "MATCH (u:User) WHERE ID(u) = $user_id "
            "CREATE (p:Post {title: $title, content: $content})-[:CREATED_BY]->(u)",
            user_id=user_id, title=title, content=content
        )
        session.close()

    return jsonify({'message': 'Post created and linked to the user successfully'}), 200

# API route to update a user
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')

    with driver.session() as session:
        session.run(
            "MATCH (u:User) WHERE ID(u) = $user_id "
            "SET u.username = $new_username, u.email = $new_email",
            user_id=user_id, new_username=new_username, new_email=new_email
        )
        session.close()

    return jsonify({'message': 'User updated successfully'}), 200

# API route to update a post
@app.route('/post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    new_title = data.get('title')
    new_content = data.get('content')

    with driver.session() as session:
        session.run(
            "MATCH (p:Post) WHERE ID(p) = $post_id "
            "SET p.title = $new_title, p.content = $new_content",
            post_id=post_id, new_title=new_title, new_content=new_content
        )
        session.close()

    return jsonify({'message': 'Post updated successfully'}), 200

# API route to delete a user
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with driver.session() as session:
        session.run("MATCH (u:User) WHERE id(u) = $user_id DETACH DELETE u", user_id=user_id)
        session.close()

    return jsonify({'message': 'User deleted successfully'}), 200

# API route to delete a post
@app.route('/post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    with driver.session() as session:
        session.run("MATCH (p:Post) WHERE ID(p) = $post_id DETACH DELETE p", post_id=post_id)
        session.close()

    return jsonify({'message': 'Post deleted successfully'}), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        with driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u.username AS username, u.email AS email")
            users = [{'username': record['username'], 'email': record['email']} for record in result]
            return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        

# API route to get a specific user
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with driver.session() as session:
        result = session.run("MATCH (u:User) WHERE ID(u) = $user_id RETURN u", user_id=user_id)
        user = result.single()["u"] if result.single() else None
        if user:
            session.close()
            return jsonify({'user': user}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

# API route to get all posts
@app.route('/posts', methods=['GET'])
def get_all_posts():
    with driver.session() as session:
        result = session.run("MATCH (p:Post) RETURN p")
        session.close()
        return jsonify({'posts': [record["p"] for record in result]})

# API route to get a specific post
@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    with driver.session() as session:
        result = session.run("MATCH (p:Post) WHERE ID(p) = $post_id RETURN p", post_id=post_id)
        post = result.single()["p"] if result.single() else None
        if post:
            session.close()
            return jsonify({'post': post}), 200
        else:
            return jsonify({'message': 'Post not found'}), 404
    

if __name__ == '__main__':
    app.run(port=8000)




