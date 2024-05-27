var vm = new Vue({
    el: '#app',
     delimiters: ['[[', ']]'],
    data: {
        host,
        username: '',
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        cart: [],
        total_selected_count: 0,
        origin_input: 0 // 用于记录手动输入前的值
    },
    computed: {
        total_count: function(){
            var total = 0;
            for(var i=0; i<this.cart.length; i++){
                total += (this.cart[i].count);
                this.cart[i].amount = ((this.cart[i].price) * (this.cart[i].count)).toFixed(2);
            }
            return total;
        },
        total_selected_amount: function(){
            var total = 0;
            this.total_selected_count = 0;
            for(var i=0; i<this.cart.length; i++){
                if(this.cart[i].selected) {
                    total += ((this.cart[i].price) * (this.cart[i].count));
                    this.total_selected_count += (this.cart[i].count);
                }
            }
            return total.toFixed(2);
        },
        selected_all: function(){
            var selected=true;
            for(var i=0; i<this.cart.length; i++){
                if(this.cart[i].selected==false){
                    selected=false;
                    break;
                }
            }
            return selected;
        }
    },
    mounted: function(){

        this.username = getCookie('username')

        // 获取购物车数据
        axios.get(this.host+'/carts/', {
                responseType: 'json',
                withCredentials: true
            })
            .then(response => {
                this.cart = response.data.cart_skus;
                for(var i=0; i<this.cart.length; i++){
                    this.cart[i].amount = ((this.cart[i].price) * this.cart[i].count).toFixed(2);
                }
            })
            .catch(error => {
                console.log(error.response.data);
            })
    },
    methods: {
        // 退出
        logoutfunc: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 减少操作
        on_minus: function(index){
            if (this.cart[index].count > 1) {
                var count = this.cart[index].count - 1;
                this.update_count(index, count);
            }
        },
        on_add: function(index){
            var count = this.cart[index].count + 1;
            this.update_count(index, count);
        },
        // 删除购物车数据
        on_delete: function(index){
            axios.delete(this.host+'/carts/', {
                    data: {
                        sku_id: this.cart[index].id
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    if (response.data.code == 0) {
                        this.cart.splice(index, 1);
                    }
                })
                .catch(error => {
                    console.log(error);
                })
        },
        on_input: function(index){
            var val = parseInt(this.cart[index].count);
            if (isNaN(val) || val <= 0) {
                this.cart[index].count = this.origin_input;
            } else {
                // 更新购物车数据
                axios.put(this.host+'/carts/', {
                        sku_id: this.cart[index].id,
                        count: val,
                        selected: this.cart[index].selected
                    }, {
                        responseType: 'json',
                        withCredentials: true
                    })
                    .then(response => {
                        this.cart[index].count = response.data.count;
                    })
                    .catch(error => {
                        console.log(error)
                    })
            }
        },
        // 更新购物车数据
        update_count: function(index, count){
            axios.put(this.host+'/carts/', {
                    sku_id: this.cart[index].id,
                    count,
                    selected: this.cart[index].selected
                }, {
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart[index].count = response.data.cart_sku.count;
                })
                .catch(error => {
                    console.log(error)
                })
        },
        // 更新购物车数据
        update_selected: function(index) {
            axios.put(this.host+'/carts/', {
                    sku_id: this.cart[index].id,
                    count: this.cart[index].count,
                    selected: this.cart[index].selected
                }, {
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart[index].selected = response.data.cart_sku.selected;
                })
                .catch(error => {
                    console.log(error);
                })
        },
        // 购物车全选
        on_selected_all: function(){
            var selected = !this.selected_all;
            axios.put(this.host + '/carts/selection/', {
                    selected
                }, {
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    for (var i=0; i<this.cart.length;i++){
                        this.cart[i].selected = selected;
                    }
                })
                .catch(error => {
                    console.log(error);
                })
        },
    }
});