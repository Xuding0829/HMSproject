package com.example.hmsproject.Utils

// MqttHelper.kt

import android.content.ContentValues.TAG
import android.util.Log
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.MqttCallback
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttException
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit

class MqttHelper(private val mqttId: String,
                 private val subscriptionTopics: List<String>,
                 private val publishTopics: List<String>) {

    private val host: String = "tcp://54.244.173.190:1883" // 例如 "tcp://mqtt.example.com:1883"
    private var client: MqttClient? = null
    private var options: MqttConnectOptions? = null

    // 创建一个单线程的定时任务执行器
    private val scheduler: ScheduledExecutorService = Executors.newSingleThreadScheduledExecutor()
    // 初始化块，在对象实例化时立即执行，用于设置 MQTT 客户端并连接
    init {
        setupMqttClient()  // 调用设置 MQTT 客户端的方法
        connect()           // 调用连接 MQTT 服务器的方法
    }

    // 设置 MQTT 客户端的方法
    private fun setupMqttClient() {
        try {
            // 创建 MQTT 客户端对象，指定主机地址、客户端 ID 和持久性存储
            client = MqttClient(host, mqttId, MemoryPersistence())
            // 创建 MQTT 连接选项对象，并进行相应配置
            options = MqttConnectOptions().apply {
                isCleanSession = true   // 设置是否清除会话状态
                connectionTimeout = 10 // 设置连接超时时间（单位：秒）
                keepAliveInterval = 20 // 设置心跳间隔时间（单位：秒）

            }

            client?.setCallback(object : MqttCallback {
                override fun connectionLost(cause: Throwable) {
                    println("连接失败，尝试重连")
                    startReconnect()
                }

                override fun messageArrived(topic: String, message: MqttMessage) {
                    println("消息来自： $topic: $message")


                }

                override fun deliveryComplete(token: IMqttDeliveryToken) {
                    println("令牌来自: ${token.messageId}")
                }
            })
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }


    private fun connect() {
        try {
            if (!client!!.isConnected) {
                client!!.connect(options)
                subscriptionTopics.forEach { topic ->
                    client!!.subscribe(topic)
                }
            }
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }


    fun startReconnect() {
        scheduler.scheduleAtFixedRate({
            if (!client!!.isConnected) {
                try {
                    connect()
                } catch (e: MqttException) {
                    println("Reconnect attempt failed: ${e.message}")
                    // 错误处理逻辑
                }
            }
        }, 0, 10, TimeUnit.SECONDS)
    }


    fun publishMessage(topic: String, messageStr: String) {  //发布消息的方法，发布主题＋消息
        if (publishTopics.contains(topic)) {
            val message = MqttMessage()
            message.payload = messageStr.toByteArray()
            try {
                client?.publish(topic, message)
            } catch (e: MqttException) {
                e.printStackTrace()
            }
        } else {
            println("主题 $topic 不在可发布列表主题内.")
        }
    }


    fun subscribeToTopic(topic: String, qos: Int) {    //订阅主题的方法
        try {
            if (client?.isConnected == true) {
                client?.subscribe(topic, qos)
                Log.d(TAG, "Subscribed to $topic")
            } else {
               Log.d(TAG,"客户端未连接，未收到订阅主题： $topic.")
            }
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }

    fun setCallback(callback: MqttCallback) {
        client?.setCallback(callback)
    }




    fun disconnect() {
        try {
            if (client?.isConnected == true) {
                // Unsubscribe from all subscribed topics before disconnecting
                subscriptionTopics.forEach { topic ->
                    client?.unsubscribe(topic)
                }

                // Disconnect the MQTT client
                client?.disconnect()

                println("Disconnected from MQTT broker.")
            }
        } catch (e: MqttException) {
            e.printStackTrace()
            println("Error occurred during MQTT disconnection: ${e.message}")
        } finally {

            client?.close()
        }
    }








}










