import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import VueSocketIO from 'vue-socket.io';
import Vuesax from 'vuesax'

import 'vuesax/dist/vuesax.css' 
import './assets/css/boxicons.min.css'

Vue.use(Vuesax, {
  // options here
})

Vue.use(new VueSocketIO({
  debug: true,
  connection: 'http://127.0.0.1:5000/internal'
}));

Vue.config.productionTip = false

Vue.use(VueAxios, axios)

new Vue({
  render: h => h(App),
}).$mount('#app')
