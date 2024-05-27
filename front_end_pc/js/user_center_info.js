var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: '',
        mobile: '',
        email: '',
        email_active: false,
        set_email: false,
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        email_error: false,
        histories: [],
    },
    mounted: function () {
        // 获取cookie中的用户名
        this.username = getCookie('username');

        // 获取个人信息:
        this.get_person_info()

        this.get_history()
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
        get_history:function(){
             // 添加下列代码, 发送请求, 获取用户的浏览记录信息:
            axios.get(this.host + '/browse_histories/', {
                    responseType: 'json',
                    withCredentials:true,
                })
                .then(response => {
                    this.histories = response.data.skus;
                    for(var i=0; i<this.histories.length; i++){
                      this.histories[i].url='/goods/'+this.histories[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error)
                });
        },
        // 获取用户所有的资料
        get_person_info: function () {
            var url = this.host + '/info/';
            axios.get(url, {
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    if (response.data.code == 400) {
                        location.href = 'login.html'
                        return
                    }
                    this.username = response.data.info_data.username;
                    this.mobile = response.data.info_data.mobile;
                    this.email = response.data.info_data.email;
                    this.email_active = response.data.info_data.email_active;
                })
                .catch(error => {
                    this.set_email = false
                    location.href = 'login.html'
                })
        },
        // 保存email
        save_email: function () {
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.email_error = false;
            } else {
                this.email_error = true;
                return;
            }

            // 进行前端页面请求:
            var url = this.host + '/emails/'
            axios.put(url,
                {
                    email: this.email
                },
                {
                    responseType: 'json',
                    withCredentials:true,
                })
                // 成功请求的回调
                .then(response => {
                    this.set_email = false;
                    this.send_email_btn_disabled = true;
                    this.send_email_tip = '已发送验证邮件'
                })
                // 失败请求的回调:
                .catch(error => {
                    alert('请求失败, 失败原因:', error);
                });
        }
    }
});