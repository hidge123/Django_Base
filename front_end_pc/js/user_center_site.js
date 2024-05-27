var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        is_show_edit: false,
        provinces: [],
        cities: [],
        districts: [],
        addresses: {},
        limit: '',
        default_address_id: '',
        form_address: {
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        },
        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_email: false,
        editing_address_index: '', // 正在编辑的地址在addresses中的下标，''表示新增地址
        is_set_title: [],
        input_title: '',
        username: ''
    },
    mounted: function () {
        // 获取cookie中的用户名
        this.username = getCookie('username');

        // 获取地址页中的地址
        this.get_address();

        // 获取省份数据:
        this.get_province();

    },
    watch: {
        'form_address.province_id': function () {
            if (this.form_address.province_id) {
                axios.get(this.host + '/areas/' + this.form_address.province_id + '/', {
                    responseType: 'json',
                    withCredentials:true,
                })
                    .then(response => {
                        this.cities = response.data.sub_data.subs;
                        this.districts = [];
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.cities = [];
                        this.districts = [];
                    });
            }
        },
        'form_address.city_id': function () {
            if (this.form_address.city_id) {
                axios.get(this.host + '/areas/' + this.form_address.city_id + '/', {
                    responseType: 'json',
                    withCredentials:true,
                })
                    .then(response => {
                        this.districts = response.data.sub_data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.districts = [];
                    });
            }
        }
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
        get_province: function () {
            axios.get(this.host + '/areas/', {
                responseType: 'json',
                withCredentials:true,
            })
                .then(response => {
                    this.provinces = response.data.province_list;
                })
                .catch(error => {
                    alert(error.response.data);
                });
        },
        clear_all_errors: function () {
            this.error_receiver = false;
            this.error_mobile = false;
            this.error_place = false;
            this.error_email = false;
        },
        // 展示新增地址界面
        show_add: function () {
            this.clear_all_errors();
            this.editing_address_index = '';
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.is_show_edit = true;
        },
        // 展示编辑地址界面
        show_edit: function (index) {
            this.clear_all_errors();
            this.editing_address_index = index + 1;
            // 只获取数据，防止修改form_address影响到addresses数据
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]));
            this.is_show_edit = true;
        },
        check_receiver: function () {
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },
        check_place: function () {
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },
        check_mobile: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        check_email: function () {
            if (this.form_address.email) {
                var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if (re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            }
        },
        // 保存地址
        save_address: function () {
            if (this.error_receiver || this.error_place || this.error_mobile || this.error_email || !this.form_address.province_id || !this.form_address.city_id || !this.form_address.district_id) {
                alert('信息填写有误！');
            } else {
                this.form_address.title = this.form_address.receiver;
                if (this.editing_address_index === '') {
                    // 新增地址
                    var url = this.host + '/addresses/create/'
                    axios.post(url, this.form_address, {
                        responseType: 'json',
                        withCredentials: true
                    })
                        .then(response => {
                            // 将新地址添加大数组头部
                            this.addresses = response.data.address;
                            this.is_show_edit = false;
                            location.href = 'user_center_site.html'
                        })
                        .catch(error => {
                            console.log(error);
                        })
                } else {

                    // 修改地址
                    var url = this.host + '/addresses/' + this.addresses[this.editing_address_index - 1].id + '/'
                    axios.put(url, this.form_address, {
                        responseType: 'json',
                        withCredentials:true,
                    })
                        .then(response => {
                            this.addresses[this.editing_address_index - 1] = response.data.address;
                            this.is_show_edit = false;
                        })
                        .catch(error => {
                            alert(error.response.data.detail || error.response.data.message);
                        })
                }
            }
        },
        // 删除地址
        del_address: function (index) {
            axios.delete(this.host + '/addresses/' + this.addresses[index].id + '/', {
                withCredentials:true,
                responseType: 'json'
            })
                .then(response => {
                    // // 从数组中移除地址
                    // this.addresses.splice(index, 1);
                    if (response.data.code == 0) {
                        location.href = 'http://www.meiduo.site:8080/user_center_site.html'
                    }

                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 获取地址数据:
        get_address: function () {
            axios.get(this.host + '/addresses/', {
                responseType: 'json',
                withCredentials:true
            })
                .then(response => {
                    this.addresses = response.data.addresses;
                    // this.limit = response.data.limit;
                    this.default_address_id = response.data.default_address_id;
                })
                .catch(error => {
                    status = error.response.status;
                    if (status == 401 || status == 403) {
                        location.href = 'login.html?next=/user_center_site.html';
                    } else {
                        // alert(error.response.data.detail);
                    }
                })
        },
        // 设置默认地址
        set_default: function (index) {
            var url = this.host + '/addresses/' + this.addresses[index].id + '/default/'
             axios.put(url, {}, {
                        responseType: 'json',
                        withCredentials:true,
                    })
                .then(response => {
                    // this.default_address_id = this.addresses[index].id;
                    if (response.data.code == 0) {
                        location.href = 'http://www.meiduo.site:8080/user_center_site.html'
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 展示编辑标题
        show_edit_title: function (index) {
            this.input_title = this.addresses[index].title;
            for (var i = 0; i < index; i++) {
                this.is_set_title.push(false);
            }
            this.is_set_title.push(true);
        },
        // 保存地址标题
        save_title: function (index) {
            if (!this.input_title) {
                alert("请填写标题后再保存！");
            } else {
                axios.put(this.host + '/addresses/' + this.addresses[index].id + '/title/', {
                    title: this.input_title
                }, {
                    responseType: 'json',
                    withCredentials:true,
                })
                    .then(response => {
                        this.addresses[index].title = this.input_title;
                        this.is_set_title = [];
                    })
                    .catch(error => {
                        console.log(error.response.data);
                    })
            }
        },
        // 取消保存地址
        cancel_title: function (index) {
            this.is_set_title = [];
        }
    }
})