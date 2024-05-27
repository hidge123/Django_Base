var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        username: '',

        old_pwd: '',
        new_pwd: '',
        new_cpwd: '',

        error_opwd: false,
        error_pwd: false,
        error_cpwd: false,
    },
    mounted: function () {
        // 给 username 赋值:
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
                    location.href = 'login.html';
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        // 表单提交按钮: 更换密码
        change_password: function () {
            this.check_opwd();
            this.check_pwd();
            this.check_cpwd();

            if (this.error_opwd == true || this.error_pwd == true || this.error_cpwd == true) {
                // 不满足修改密码条件：禁用表单
                window.event.returnValue = false;
                return;
            }

            var url = this.host + '/password/';
            axios.put(url, {
                old_password:this.old_pwd,
                new_password:this.new_pwd,
                new_password2:this.new_cpwd
            }, {
                responseType: 'json',
                withCredentials: true,
            })
                .then(response => {
                    if (response.data.code == 0) {
                        location.href = 'login.html'
                    } else if (response.data.status == 400) {
                        // TODO:如果有问题, 需要报错/ 没写的:

                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }
        ,
// 检查当前密码是否正确
        check_opwd: function () {
            var re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.old_pwd)) {
                this.error_opwd = false;
            } else {
                this.error_opwd = true;
            }
        }
        ,
        check_pwd: function () {
            var re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.new_pwd)) {
                this.error_pwd = false;
            } else {
                this.error_pwd = true;
            }
        }
        ,
        // 确认密码点击事件
        check_cpwd: function () {
            if (this.new_pwd != this.new_cpwd) {
                this.error_cpwd = true;
            } else {
                this.error_cpwd = false;
            }
        }
    }
})