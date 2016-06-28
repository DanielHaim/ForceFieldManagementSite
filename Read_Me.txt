render_template('index.html',
                title='Home',
                user=user)

cette fonction va envoyer au template "index.html" la variable 'title' et 'user' de telle sorte que si dans le template il y'a marquer {{title}} et {{user}} ca va pouvoir l'afficher.