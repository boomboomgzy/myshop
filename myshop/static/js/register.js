let vm = new Vue({
    el: "#app",

    // 修改Vue读取变量的模板语法
    delimiters: ['[[', ']]'],

    data: {
        // v-model
        uuid: '',
        image_code_url: '',
        username: '',
        password: '',
        confirm_pwd: '',
        image_code: '',
        mobile: '',
        sms_code: '',
        sms_code_tip: '获取短信验证码',
        send_flag: false,   // 短信发送标记
        register_errmsg: '',
        allow: false,

        // v-show
        error_username: false,
        error_password: false,
        error_confirm_pwd: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        // 控制展示注册时的错误信息
        show_register_errmsg: false,

        // error_msg
        error_username_msg: '',
        error_mobile_msg: '',
        error_image_code_msg: '',
        error_sms_code_message: '',

    },

    // 页面加载完成后执行
    mounted() {
        // 生成图形验证码
        this.generate_image_code();
    },

    methods: {
        generate_image_code() {
            // 生成UUID。generateUUID() : 封装在common.js文件中，需要提前引入
            this.uuid = generateUUID();
            // 拼接图形验证码请求地址
            this.image_code_url = "/image_codes/" + this.uuid + "/";

        },
        check_username() {
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if (re.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_username_msg = '请输入5-20个字符的用户名';
                this.error_username = true;
            }

            if (this.error_username === false) {
                // 判断用户名是否重复注册
                let url = '/usernames/' + this.username + '/count/'
                let options = {responseType: 'json'}
                axios.get(url, options)
                    .then(response => {
                        if (response.data.data.count === 1) {
                            this.error_username_msg = '用户名已存在';
                            this.error_username = true;
                        } else {
                            this.error_username = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        check_password() {
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        check_confirm_pwd() {
            if (this.password !== this.confirm_pwd) {
                this.error_confirm_pwd = true;
            } else {
                this.error_confirm_pwd = false;
            }
        },
        check_mobile() {
            let re = /^1[3-9]\d{9}$/;

            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_msg = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }

            if (this.error_mobile === false) {
                // 校验手机号是否重复注册
                let url = '/mobiles/' + this.mobile + '/count/'
                let options = {responseType: 'json'}
                axios.get(url, options)
                    .then(response => {
                        console.log(response.data)

                        if (response.data.data.count === 1) {
                            //    手机号重复注册
                            this.error_mobile = true
                            this.error_mobile_msg = '手机号码重复注册'
                        } else {
                            this.error_mobile = false
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        check_image_code() {
            if (!this.image_code) {
                this.error_image_code_msg = '请填写图片验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        check_allow() {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        check_sms_code() {
            if (this.sms_code.length !== 6) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        send_sms_code() {
            // 避免重复点击
            if (this.sending_flag === true) {
                return;
            }
            this.sending_flag = true;

            // 校验参数
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile === true || this.error_image_code === true) {
                this.sending_flag = false;
                return;
            }

            // 请求短信验证码
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            let options = {responseType: 'json'}
            axios.get(url, options)
                .then(response => {
                    if (response.data.code === 0) {
                        // 倒计时60秒
                        var num = 60;
                        var t = setInterval(() => {
                            if (num === 1) {
                                clearInterval(t);
                                this.sms_code_tip = '获取短信验证码';
                                this.sending_flag = false;
                            } else {
                                num -= 1;
                                // 展示倒计时信息
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000, 60)
                    } else {
                        if (response.data.code === 4001) {
                            this.error_image_code_msg = response.data.errmsg;
                            this.error_image_code = true;
                        } else { // 4002
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.generate_image_code();
                        this.sending_flag = false;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.sending_flag = false;
                })
        },
        on_submit() {
            this.check_username();
            this.check_password();
            this.check_confirm_pwd();
            this.check_mobile();
            this.check_allow();

            if (this.error_username === true || this.error_password === true || this.error_confirm_pwd === true
                || this.error_mobile === true || this.error_allow === true) {
                // 禁用表单的提交
                window.event.returnValue = false;
                console.log('args error')
            } else {
                console.log('register')
            }
        },
    },


})