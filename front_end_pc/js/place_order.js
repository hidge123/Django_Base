var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: '',
        skus: [],
        freight: 0, // 运费
        total_count: 0,
        total_amount: 0,
        payment_amount: 0,
        order_submitting: false, // 正在提交订单标志
        pay_method: 1, // 支付方式,
        nowsite:0, // 默认地址
        addresses: []
    },
    mounted: function(){
        this.username = getCookie('username')

        // 获取结算商品信息
        axios.get(this.host+'/orders/settlement/', {
                responseType: 'json',
                withCredentials:true
            })
            .then(response => {
                this.skus = response.data.context.skus;
                this.freight = response.data.context.freight;
                this.addresses = response.data.context.addresses;
                this.total_count = 0;
                this.total_amount = 0;
                for(var i=0; i<this.skus.length; i++){
                    var amount = parseFloat(this.skus[i].price)*this.skus[i].count;
                    this.skus[i].amount = amount.toFixed(2);
                    this.total_count += this.skus[i].count;
                    this.total_amount += amount;
                }
                this.payment_amount = parseFloat(this.freight) + this.total_amount;
                this.payment_amount = this.payment_amount.toFixed(2);
                this.total_amount = this.total_amount.toFixed(2);
            })
            .catch(error => {
                if (error.response.status == 401){
                    location.href = '/login.html?next=/cart.html';
                } else{
                    console.log(error);
                }
            })
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
                    location.href = 'login.html';
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
         // 提交订单
        on_order_submit: function(){
                var url = this.host+'/orders/commit/'
                axios.post(url, {
                        address_id: this.nowsite,
                        pay_method: Number(this.pay_method)
                    }, {
                        withCredentials:true,
                        responseType: 'json'
                    })
                    .then(response => {
                        if (response.data.code == 0){
                              location.href = '/order_success.html?order_id='+response.data.order_id
                            +'&amount='+this.payment_amount
                            +'&pay='+this.pay_method;
                        } else if (response.data.code == 400){
                            alert(response.data.errmsg)
                        }

                    })
                    .catch(error => {
                        this.order_submitting = false;
                        alert(error);
                    })
        }
    }
});