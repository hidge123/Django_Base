var vm = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        host,
        username: '',
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        order_id: '',
        amount: 0,
        pay_method: '',
    },
    computed: {
        operate: function(){
            if (this.pay_method==1){
                return '继续购物';
            } else {
                return '去支付';
            }
        }
    },
    mounted: function(){
        this.order_id = this.get_query_string('order_id');
        this.amount = this.get_query_string('amount');
        this.pay_method = this.get_query_string('pay');

          // 获取cookie中的用户名
    	this.username = getCookie('username');

    },
    methods: {
        // 退出登录按钮
        logoutfunc: function () {
            var url = this.host + '/logout/';
            axios.delete(url, {
                responseType: 'json',
                withCredentials:true,
            })
                .then(response => {
                    if (response.data.code == 1) {
                        location.href = 'login.html';
                    } else {
                        alert(response.data.errmsg)
                    }
                })
                .catch(error => {
                    console.log(error);
                })
        },
        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
         next_operate: function(){
            if (this.pay_method == 1) {
                location.href = '/index.html';
            } else {
                // 发起支付
                var url = this.host+'/payment/'+this.order_id+'/'
                axios.get(url, {
                        withCredentials:true,
                        responseType: 'json'
                    })
                    .then(response => {
                        // 跳转到支付宝支付
                         if (response.data.code == 0) {
                            location.href = response.data.alipay_url;
                        } else {
                            alert(response.data.errmsg)
                        }
                    })
                    .catch(error => {
                        console.log(error);
                    })
            }
        }
    }
});