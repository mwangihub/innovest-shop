const sync = {

    getCookie: (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    ws: () => {
        let http = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        var socket = new WebSocket(http + window.location.host + window.location.pathname);
        return socket
    },

    sendRequest: (method, url, data) => {
        console.log(data);
        // Remember there is use of Async for best performance in the callee of this.
        //create a new promise object then promisify the XMLHTTResuest with resolve and reject
        const promise = new Promise((resolve, reject) => {
            var xhr = new XMLHttpRequest();
            xhr.open(method, url);
            // Required by Django
            xhr.setRequestHeader('HTTP_X_REQUEST_WITH', 'XMLHttpRequest');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            // Django needs csrf token
            xhr.setRequestHeader("X-CSRFToken", sync.getCookie("csrftoken"));
            xhr.onload = () => {
                    //We have to check for status codes here from the server then reject them or resolve
                    // However Django can be set to do that by logically handling that in the backend hence,
                    // no need to write all status codes here with if else 
                    if (xhr.status >= 400) reject(xhr.response);
                    // For the case of django returns this
                    // return JsonResponse(serialized, status=200, safe=False)
                    if (xhr.status === 200) resolve(xhr.response)
                }
                //  For failure of network connection but not from the server
            xhr.onerror = () => {
                    reject('Something went wrong!')
                }
                //not neccesary. Just for testing
                // data = { 'request': 'I am requesting to delete this' }
                //we only send JSON data if we passed real data
            if (data) xhr.send(JSON.stringify(data));
            else xhr.send();
        });
        return promise
    },
}


















// sendPaypalBackEnd: (url, dict) => {
//     sync.sendRequest('POST', url, dict).then(response => {
//         var data = JSON.parse(response)
//         window.location.href = `${window.location.origin}/innovest-view-detail/`;
//         if (data.success) {
//             console.log(data);
//         }

//     }).catch(error => {
//         console.log(error);
//     });
// },

// sendPayPalPaypal: (amount) => {
//     let amt = parseFloat(amount.innerHTML).toFixed(2);
//     const buttons = paypal.Buttons({
//         style: {
//             color: 'blue'
//         },
//         createOrder: function(data, actions) {
//             return actions.order.create({
//                 purchase_units: [{
//                     amount: {
//                         value: amt
//                     }
//                 }]
//             });
//         },
//         onApprove: function(data, actions) {
//             return actions.order.capture().then(function(orderData) {
//                 sync.sendRequest('POST', window.location.pathname, orderData).then(response => {
//                     var datas = JSON.parse(response)
//                     window.location.href = `${window.location.origin}/innovest-view-detail/`;
//                 }).catch(error => {
//                     console.log(error);
//                 });

//             });
//         }
//     }).render('#paypal-button-container');
//     return buttons
// },