import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import VueSocketIO from 'vue-socket.io';
import Vuesax from 'vuesax'

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

process.argv.forEach((val, index) => {
  console.log(`${index}: ${val}`);
});

Vue.use(new VueSocketIO({
  debug: true,
  connection: process.env.VUE_APP_API_URL + '/internal'
}));

Vue.config.productionTip = false

Vue.use(VueAxios, axios)

Vue.axios.defaults.baseURL = process.env.VUE_APP_API_URL;

new Vue({
  render: h => h(App),
}).$mount('#app')
