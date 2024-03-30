db.createUser(
    {
        user: 'app_user',
        pwd: 'password',
        roles: [
            {role: 'readWrite', db: 'your_app'},
            {role: 'readWrite', db: 'test_your_app'},
        ],
    },
);
