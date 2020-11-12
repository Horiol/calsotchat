import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import VueSocketIO from 'vue-socket.io';
import Vuesax from 'vuesax'
import { ipcRenderer } from 'electron'

import 'vuesax/dist/vuesax.css' 
import './assets/css/boxicons.min.css'

Vue.use(Vuesax, {
  colors: {
    primary:'#59316B',
    dark: '#333A41',
    success:'#68B030',
    text:'#59316B'

    // primary:'#5b3cc4',
    // success:'rgb(23, 201, 100)',
    // danger:'rgb(242, 19, 93)',
    // warning:'rgb(255, 130, 0)',
    // dark:'rgb(36, 33, 69)'
  }
})

Vue.config.productionTip = (process.env.NODE_ENV == "production")

Vue.use(VueAxios, axios)

var url = "http://localhost:5000/api"
if (process.env.IS_ELECTRON){
  url = ipcRenderer.sendSync('get-api-url')
}else{
  console.log("TODO");
}
Vue.axios.defaults.baseURL = url;

Vue.use(new VueSocketIO({
  debug: !(process.env.NODE_ENV == "production"),
  connection: url + '/internal'
}));

new Vue({
  render: h => h(App),
}).$mount('#app')
