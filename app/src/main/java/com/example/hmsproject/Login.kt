package com.example.hmsproject


import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class Login : AppCompatActivity() {

    private lateinit var usernameEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var autoLoginCheckBox: CheckBox
    private lateinit var loginButton: Button
    private lateinit var registerButton: Button
    private lateinit var sharedPreferences: SharedPreferences

    // 创建活动
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        // 初始化数据
        init()

        // 检查登录状态
        val isLoggedIn = sharedPreferences.getBoolean("loggedIn", false)
        if (isLoggedIn) {
            // 自动跳转到新界面
            val intent = Intent(this, ListView::class.java)
            startActivity(intent)
            finish()
        }

        // 登录按钮点击事件
        loginButton.setOnClickListener {
            val username = usernameEditText.text.toString()
            val password = passwordEditText.text.toString()
            if (username.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "请输入用户名和密码", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // 检查用户名和密码是否正确
            if (checkUsernameAndPassword(username, password)) {
                // 登录成功
                Toast.makeText(this, "登录成功", Toast.LENGTH_SHORT).show()

                if (autoLoginCheckBox.isChecked) {
                    // 保存登录状态
                    val editor = sharedPreferences.edit()
                    editor.putBoolean("loggedIn", true)
                    editor.apply()
                }

                // 跳转到新界面
                val intent = Intent(this, ListView::class.java)
                startActivity(intent)
                finish()
            } else {
                // 登录失败
                Toast.makeText(this, "用户名或密码错误", Toast.LENGTH_SHORT).show()
            }
        }

        // 注册按钮点击事件
        registerButton.setOnClickListener {
            val username = usernameEditText.text.toString()
            val password = passwordEditText.text.toString()

            // 检查用户名是否已经存在
            if (checkIfUserExists(username)) {
                // 用户已经存在
                Toast.makeText(this, "用户已存在", Toast.LENGTH_SHORT).show()
            } else {
                // 注册成功
                Toast.makeText(this, "注册成功", Toast.LENGTH_SHORT).show()
                // 保存用户信息
                val editor = sharedPreferences.edit()
                editor.putString("username", username)
                editor.putString("password", password)
                editor.apply()

                // 跳转到新界面
                val intent = Intent(this, Login::class.java)
                startActivity(intent)
                finish()
            }
        }
    }

    // 检查用户名和密码是否正确
    private fun checkUsernameAndPassword(userName: String, password: String): Boolean {
        val sUsername = sharedPreferences.getString("username", "")
        val sPassword = sharedPreferences.getString("password", "")
        return userName == sUsername && password == sPassword
    }

    // 检查用户名是否已经存在
    private fun checkIfUserExists(userName: String): Boolean {
        val sUsername = sharedPreferences.getString("username", "")
        return userName == sUsername
    }

    // 初始化数据
    private fun init() {
        usernameEditText = findViewById(R.id.username)
        passwordEditText = findViewById(R.id.password)
        autoLoginCheckBox = findViewById(R.id.auto_login)
        loginButton = findViewById(R.id.login)
        registerButton = findViewById(R.id.register)
        sharedPreferences = getSharedPreferences("userInfo", Context.MODE_PRIVATE)
    }
}
