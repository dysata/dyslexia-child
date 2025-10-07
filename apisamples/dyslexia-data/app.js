//test credentials
//couchdb admin:couchdbpasswd

var basic_api_token = "test_token";
var nextcloud_url = 'http://localhost/nextcloud/remote.php/dav/files/nextclouduser/dyslexia';
var nextcloud_user = 'nextclouduser';
var nextcloud_password = 'nextcloudpassword';

var couchdb_url = 'http://localhost:5984';
var couchdb_user = 'admin';
var couchdb_password = 'couchdbadmin';

var mongoHost = "mongodb://localhost/dyslexia";

//CONFIGURATION: obtain and set your telegram token:
//https://core.telegram.org/bots/tutorial
var telegram_token = '5957043845:AAF7X7BhFBRNCz0CxN1s55kG0Vfk1POH-5A';

var telegram_dyslexia_text = 'Текст про раков или другой, который нужно начитывать';




'use strict'

/**
 * Module dependencies.
 */

var express = require('express');
var hash = require('pbkdf2-password')()
var path = require('path');
var session = require('express-session');

var app = module.exports = express();

app.use('/static', express.static('public'));

// config

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// middleware

app.use(express.urlencoded({ extended: false }))
app.use(session({
  resave: false, // don't save session if unmodified
  saveUninitialized: false, // don't create session until something stored
  secret: 'some secret here'
}));

// Session-persisted message middleware

app.use(function(req, res, next){
  var err = req.session.error;
  var msg = req.session.success;
  delete req.session.error;
  delete req.session.success;
  res.locals.message = '';
  if (err) res.locals.message = '<p class="msg error">' + err + '</p>';
  if (msg) res.locals.message = '<p class="msg success">' + msg + '</p>';
  next();
});

//TODO: we demonstrate basic usage with a user 'user'
//Arrange user managment with some real database to store users

//////////////// Example authentication scheme //////////////////////

var users = {
  user: { name: 'user' }
};

// when you create a user, generate a salt
// and hash the password ('password' is the pass here)

let crypto = require('crypto');

let hasher = (password, salt) => {
  let hash = crypto.createHmac('sha512', salt);
  hash.update(password);
  let value = hash.digest('hex');
  return {
      salt: salt,
      hashedpassword: value
  };
};

var d = hasher('password', 'salt');
users.user.salt = d.salt;
users.user.hash = d.hashedpassword;

function authenticate(name, pass, fn) {
  var user = users[name];
  console.log(user)
  // query the db for the given username
  if (!user) return fn(null, null)
  // apply the same algorithm to the POSTed password, applying
  // the hash against the pass / salt, if there is a match we
  // found the user
  var d = hasher(pass, user.salt);
  if(d.hashedpassword === user.hash) 
    fn(null, user);
  else
    fn(null, null);
}

function restrict(req, res, next) {
  if (req.session.user) {
    next();
  } else {
    req.session.error = 'Access denied!';
    res.redirect('/login');
  }
}

app.get('/', function(req, res){
  res.redirect('/login');
});

app.get('/widgets', restrict, function(req, res){
  res.render('index');
});

app.get('/logout', function(req, res){
  // destroy the user's session to log them out
  // will be re-created next request
  req.session.destroy(function(){
    res.redirect('/');
  });
});

app.get('/login', function(req, res){
  res.render('login');
});

const auth = require('basic-auth')

app.get('/tokens', function (req, res, next) {
  var credentials = auth(req);
  authenticate(credentials.name, credentials.pass, function (err, user){
    if(err) return next(err);
    if(user) {
      // Regenerate session when signing in
      // to prevent fixation
      req.session.regenerate(function(){
        // Store the user's primary key
        // in the session store to be retrieved,
        // or in this case the entire user object
        req.session.user = user;
        req.session.success = "ok";
        res.setHeader('Content-Type', 'application/json');
        res.status(200).send(JSON.stringify({ tokens : [{ user_id :  0, token : 'some token here'}] }));
      });
    } else {
      req.session.error = '401';
      res.status(401).send('Unauthorized');
    }
  });      
});

app.post('/login', function (req, res, next) {
  authenticate(req.body.username, req.body.password, function(err, user){
    if (err) return next(err)
    if (user) {
      // Regenerate session when signing in
      // to prevent fixation
      req.session.regenerate(function(){
        // Store the user's primary key
        // in the session store to be retrieved,
        // or in this case the entire user object
        req.session.user = user;
        req.session.success = 'Authenticated as ' + user.name
          + ' click to <a href="/logout">logout</a>. '
          + ' You may now access all <a href="/widgets">/widgets</a>.';
        res.redirect('back');
      });
    } else {
      req.session.error = 'Authentication failed, please check your '
        + ' username and password.'
      res.redirect('/login');
    }
  });
});



var morgan = require('morgan')
app.use(morgan('dev'));


const { createProxyMiddleware } = require('http-proxy-middleware');
// proxy middleware options

// //-------------------- proxy for couchDB  -----------------------------
const couchdb_proxy_options = {
  target : couchdb_url,
  changeOrigin : true, // needed for virtual hosted sites
  auth : couchdb_user + ':' + couchdb_password,
  logLevel:"debug",
  pathRewrite: {'^/couchdb' : ''},
  onProxyReq(proxyReq, req, res) {
      if (!req.session.user) {
          res.status(401).send('Authentication error');
          return;
      }
  }
};

// create the proxy (without context)
const couchdb_proxy = createProxyMiddleware(couchdb_proxy_options);

// mount `exampleProxy` in web server

app.use('/couchdb', couchdb_proxy);

// //------------------- proxy for couchDB --------------------------

// //-------------------- proxy for nextcloud -----------------------------
// proxy middleware options

const nextcloud_proxy_options = {
  target: nextcloud_url,
  changeOrigin: true, // needed for virtual hosted sites
  auth: nextcloud_user + ':' + nextcloud_password,
  logLevel:"debug",
  pathRewrite: {'^/storage' : ''},
  secure: false,
  onProxyReq(proxyReq, req, res) {
      if (!req.session.user) {
      res.status(401).send('Authentication error');
          return;
      }
  }
};

// create the proxy (without context)
const nextcloud_proxy = createProxyMiddleware(nextcloud_proxy_options);

// mount `exampleProxy` in web server
app.use('/storage', nextcloud_proxy);

// //------------------- proxy for nextcloud --------------------------


//////////////////////// Neuroscience bot /////////////////////

const TelegramBot = require('node-telegram-bot-api');

const neural_bot_token = telegram_token;

const neural_bot = new TelegramBot (neural_bot_token, {
  polling:true,
  filepath:true
});

const neural_bot_commands = ['/start'];

var neural_chats = {};

function neural_bot_init(msg){

	if(! (msg.chat.id in neural_chats))
		neural_chats[msg.chat.id] = {
			status : "Working",
			results : {
				age : null,
				sex : null,
				audio : []
			}
		};
	neural_chats[msg.chat.id]['last_msg'] = msg;
	var reply = "Здравствуйте! Не понимаю произвольные сообщения. Воспользуйтесь меню.";
	var options = {
					reply_markup: {
					keyboard: [
                      ["Возраст", "Пол"]
                    ],
					force_reply: true,
					one_time_keyboard: true
                  }
  };
  neural_bot.sendMessage(msg.chat.id, reply, options);
}

neural_bot.onText(/\/start/, msg => {
  console.log("Telegram Input Message: " + JSON.stringify(msg));
  neural_bot_init(msg);
});

function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

neural_bot.on('message', (msg) => {
	console.log("Msg: " + JSON.stringify(msg));
	if('text' in msg) {
		var first_word = msg.text.split(' ')[0];
		//if command, do not process
		if(neural_bot_commands.includes(first_word))
			return;
	}

	var reply = "";
	var options = {};
	if(! (msg.chat.id in neural_chats)) {
		neural_bot_init(msg);
	} else  {
		if('text' in msg) {
			console.log("Text = ");
			console.log(msg.text);
			if(neural_chats[msg.chat.id].status == 'Working') {
				if(msg.text == "Возраст") {
					console.log("processing Age");
					neural_chats[msg.chat.id].status = 'Age';
					reply = "Укажите возраст:";
/*					var keyboard = [
						['7', '8', '9'],
						['4', '5', '6'],
						['1', '2', '3'],
						['0']
					]; 
					options = {
						reply_markup : {
						keyboard : keyboard,
						force_reply : true,
						one_time_keyboard : true,

						}
					};
*/					
				} else if (msg.text == "Пол") {
					console.log("Processing Sex");
					neural_chats[msg.chat.id].status = 'Sex';
					reply = "Укажите пол:";
					var keyboard = [['М','Ж']];
					options = {
						reply_markup : {
						keyboard : keyboard,
						force_reply : true,
						one_time_keyboard : true
						}
					};
				} else if (msg.text == "Запись аудио") {
					console.log("Processing audio");
					neural_chats[msg.chat.id].status = 'Audio';
					reply = telegram_dyslexia_text + "\n\nПришлите аудиосообщение, в котором вы читаете приведенный выше текст\n";
					options = {
						reply_markup : {
						remove_keyboard : true
						}
					};
				} else {
					var reply = "Не понимаю произвольные сообщения. Воспользуйтесь меню.";
					var keyboard = [[]];
					var flag = true;
					if(!neural_chats[msg.chat.id].results.age) {
						keyboard[0].push('Возраст');
						flag = false;
					}
					if(!neural_chats[msg.chat.id].results.sex) {
						keyboard[0].push('Пол');
						flag = false;
					}
					if(flag)
						keyboard[0].push('Запись аудио');
					var options = {
						reply_markup: {
							keyboard: keyboard,
							force_reply: true,
							one_time_keyboard: true
						}
					};
				}
			} else if(neural_chats[msg.chat.id].status == 'Sex') {
				console.log("Sex state");
				if(msg.text == 'М' || msg.text == 'Ж') {
					neural_chats[msg.chat.id].status = 'Working';
					neural_chats[msg.chat.id].results.sex = msg.text;
					reply = "Записал Пол = " + msg.text;
					var keyboard = [[]];
					if(!neural_chats[msg.chat.id].results.age)
						keyboard[0].push('Возраст');
					else
						keyboard[0].push('Запись аудио');
					options = {
						reply_markup : {
							keyboard : keyboard,
							force_reply : true,
							one_time_keyboard : true
						}
					};
				} else {
					reply = "Укажите пол:";
					var keyboard = [['М','Ж']];
						options = {
								reply_markup : {
								keyboard : keyboard,
								force_reply : true,
								one_time_keyboard : true
							}
						};
					}
			} else if(neural_chats[msg.chat.id].status == 'Age') {
				console.log("Age state");
				const parsed = parseInt(msg.text, 10);
				if(isNaN(parsed) || parsed < 4 || parsed > 110) {
					reply = "Укажите возраст:";
/*					var keyboard = [
						['7', '8', '9'],
						['4', '5', '6'],i
						['1', '2', '3'],
						['0']
					]; 
					options = {
						reply_markup : {
						keyboard : keyboard,
						force_reply : true,
						one_time_keyboard : true
						}
					};
*/					
				} else {
					neural_chats[msg.chat.id].status = 'Working';
					neural_chats[msg.chat.id].results.age = parsed;
					reply = "Записал Возраст = " + msg.text;
					var keyboard = [[]];
					if(!neural_chats[msg.chat.id].results.sex)
						keyboard[0].push('Пол');
					else
						keyboard[0].push('Запись аудио');
					options = {
						reply_markup : {
							keyboard : keyboard,
							force_reply : true,
							one_time_keyboard : true
						}
					};
				}
			} else if(neural_chats[msg.chat.id].status == 'Запись аудио') {
				console.log("Audio state in text");
				neural_chats[msg.chat.id].status = 'Audio';
				reply = config.misc.telegram.neural.dyslexia.text + "\n\nПришлите аудиосообщение, в котором вы читаете приведенный выше текст\n";
				options = {
					reply_markup: {
						remove_keyboard : true
					}
				};
			}
		} else if('voice' in msg ) {
			if(neural_chats[msg.chat.id].status == 'Audio') {
				console.log("have to save audio");

				const readStream = neural_bot.getFileStream(msg.voice.file_id);

				console.log("got stream");

const http = require('http');
var username = 'user';
var password = 'password';
var auth = 'Basic ' + Buffer.from(username + ':' + password).toString('base64');
const req_options = {
	hostname: 'localhost',
	port: 3000,
	path: '/tokens',
	method: 'GET',
	headers : {
		'Authorization' : auth
	}
};
const req = http.request(req_options, (res) => {
	console.log('statusCode:', res.statusCode);
	console.log('headers:', res.headers);
	var cookie = res.headers['set-cookie'];
	let str = "";
	res.on('data', (d) => {
		str += d.toString();
	});
	res.on('end', function () {
		const body = JSON.parse(str);
		console.log(body);
		var filename = body.tokens[0].user_id + '-audio-telegram-' + makeid(10) + '.ogg';
		var user_id = body.tokens[0].user_id;
		const req_options = {
			hostname: 'localhost',
			port: 3000,
			path: '/storage/' + filename,
			method: 'PUT',
			headers : {
				'Content-Type' : 'audio/ogg',
				'Cookie' : cookie
			}
		};
		const req = http.request(req_options, (res) => {
			console.log('statusCode:', res.statusCode);
			console.log('headers:', res.headers);
			let str = "";
			res.on('data', (d) => {
				str += d.toString();
			});
			res.on('end', function () {
				console.log(str);
				if(res.statusCode == 201) {
					var couchdb_doc = 
							{
								'dataobject' : 
									{ 
										'files': 
											[
												{ 'path' : filename, 'mime' : "audio/ogg"}
											],
										'tags' : ['dyslexia'],
										'user_id': user_id, 
										'source' : "telegram", 
										'msg' : msg
									}
							};
					const req_options = {
						hostname: 'localhost',
						port: 3000,
						path: '/couchdb/dyslexia/',
						method: 'POST',
						headers : {
							'Content-Type' : 'application/json',
							'Cookie' : cookie
						}
					};
					const req = http.request(req_options, (res) => {
						console.log('statusCode:', res.statusCode);
						console.log('headers:', res.headers);
						let str = "";
						res.on('data', (d) => {
							str += d.toString();
						});
						res.on('end', function () {
							console.log(str);
						});
					});
					req.on('error', (e) => {
						console.log("in req error");
						console.error(e);
					});
					req.write(JSON.stringify(couchdb_doc));
					req.end();
				}
			});
		});
		req.on('error', (e) => {
			console.log("in req error");
			console.error(e);
		});
		readStream.on('end', () => req.end());
		readStream.pipe(req);
	});
});
req.on('error', (e) => {
	console.log("in req error");
	console.error(e);
});
req.end();


				neural_chats[msg.chat.id].status = 'Working';
				reply = "Сохранил аудио. Можете повторить процедуру сами или предложить пройти eё другому человеку.";
				neural_bot_init(msg)

/*				var keyboard = [[]];
				keyboard[0].push('Запись аудио');
				var options = {
					reply_markup: {
						keyboard: keyboard,
						force_reply: true,
						one_time_keyboard: true
					}
				};
*/
				
			} else {
				var reply = "Не понимаю произвольные сообщения. Воспользуйтесь меню.";
				var keyboard = [[]];
				var flag = true;
				if(!neural_chats[msg.chat.id].results.age) {
					keyboard[0].push('Возраст');
					flag = false;
				}
				if(!neural_chats[msg.chat.id].results.sex) {
					keyboard[0].push('Пол');
					flag = false;
				}
				if(flag)
					keyboard[0].push('Запись аудио');
				var options = {
					reply_markup: {
						keyboard: keyboard,
						force_reply: true,
						one_time_keyboard: false
					}
				};
			}
		}
	}
	if(reply != "") {
		neural_bot.sendMessage(msg.chat.id, reply, options);  
	}
	console.log("Reply = " + reply);
});
