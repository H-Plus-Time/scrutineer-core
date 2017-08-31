const functions = require('firebase-functions');

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
// exports.helloWorld = functions.https.onRequest((request, response) => {
//  response.send("Hello from Firebase!");
// });

exports.subscribeToTopic = functions.https.onRequest((request, response) => {
    let registrationToken = request.body.token;
    let topic = request.body.topic;
    admin.messaging().subscribeToTopic(registrationToken, topic)
    .then(function (resp) {
        // See the MessagingTopicManagementResponse reference documentation
        // for the contents of response.
        response.send(`Successfully subscribed to topic:${topic}`);
    })
    .catch(function (error) {
        response.send(`Error subscribing to topic:${topic}`);
    });
})