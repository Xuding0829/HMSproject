package com.example.hmsproject

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.PixelFormat
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.Button
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.baidu.mapapi.SDKInitializer
import com.baidu.mapapi.map.BitmapDescriptor
import com.baidu.mapapi.map.BitmapDescriptorFactory
import com.baidu.mapapi.map.MapStatusUpdateFactory
import com.baidu.mapapi.map.MapView
import com.baidu.mapapi.map.Marker
import com.baidu.mapapi.map.MarkerOptions
import com.baidu.mapapi.model.LatLng
import com.baidu.location.LocationClient;
import com.baidu.mapapi.CoordType;
import com.example.hmsproject.Utils.MqttHelper
import com.google.android.material.bottomsheet.BottomSheetDialog
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.MqttCallback
import org.eclipse.paho.client.mqttv3.MqttMessage

// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"


/**
 * A simple [Fragment] subclass.
 * Use the [Fragment2.newInstance] factory method to
 * create an instance of this fragment.
 */
class Fragment2 : Fragment() {

    private var param1: String? = null
    private var param2: String? = null
    private var mMapView: MapView? = null
    private var changebutton: Button? = null
    private lateinit var mqttHelper: MqttHelper
    var currentMarker: Marker? = null//头像标记
    override fun onCreate(savedInstanceState: Bundle?) {

        // 获取 Fragment 所在的 Activity 的窗口
        val window = requireActivity().window
        // 设置 PixelFormat 为半透明
        window.setFormat(PixelFormat.TRANSLUCENT)

        super.onCreate(savedInstanceState)

        arguments?.let {
            param1 = it.getString(ARG_PARAM1)
            param2 = it.getString(ARG_PARAM2)

        }

        mqttHelper = MqttHelper(
            mqttId = "catcyf",
            subscriptionTopics = listOf("catdingyue"),
            publishTopics = listOf("catfabu2")
        )
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        SDKInitializer.initialize(requireActivity().applicationContext)

        // 加载布局文件
        val view = inflater.inflate(R.layout.fragment_2, container, false)
        changebutton = view.findViewById(R.id.change)
        changebutton?.setOnClickListener {
            showBottomSheetDialog()
        }
        hideStatusBar3()
        // 初始化地图
        mMapView = view.findViewById(R.id.bmapView)

        locate()

        // 订阅一个主题
        mqttHelper.subscribeToTopic("catdingyue", 1)
        mqttHelper.setCallback(mqttCallback)
        return view
    }

    override fun onResume() {
        super.onResume()
        // 在Fragment执行onResume时执行mMapView.onResume()，实现地图生命周期管理
        mMapView?.onResume()
    }

    override fun onPause() {
        super.onPause()
        // 在Fragment执行onPause时执行mMapView.onPause()，实现地图生命周期管理
        mMapView?.onPause()
    }

    override fun onDestroy() {
        super.onDestroy()
        // 在Fragment执行onDestroy时执行mMapView.onDestroy()，实现地图生命周期管理
        mMapView?.onDestroy()
    }

    fun locate()
    {

    }


    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Fragment2.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Fragment2().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
    // 设置MQTT回调
    private val mqttCallback = object : MqttCallback {
        override fun messageArrived(topic: String, message: MqttMessage) {
            val msg = message.toString()

            // Logging for debugging
            Log.d("MQTT", "Received message: $msg")

            val regex = """纬度：(-?\d+\.\d+)，经度：(-?\d+\.\d+)""".toRegex()
            val matchResult = regex.find(msg)

            matchResult?.let { result ->
                val latitude = result.groupValues[1].toDoubleOrNull()
                val longitude = result.groupValues[2].toDoubleOrNull()

                if (latitude != null && longitude != null) {
                    // Logging for debugging
                    Log.d("MQTT", "Latitude: $latitude, Longitude: $longitude")
                    activity?.runOnUiThread {
                        // 移除当前的标记
                        currentMarker?.remove()
                        currentMarker = null
                        // 创建新的标记
                        val markerOptions = MarkerOptions()
                            .position(LatLng(latitude, longitude))
                            .icon(createSmallIcon2()) // 使用自定义图片

                        currentMarker = mMapView?.map?.addOverlay(markerOptions) as Marker?
                        // 构建地图状态的更新，以当前位置为中心，缩放级别为18
                        val mapStatusUpdate = MapStatusUpdateFactory.newLatLngZoom(
                            LatLng(latitude, longitude), // 设置地图中心点
                            19f // 设置缩放级别
                        )
                        // 平滑动画显示更新后的地图状态
                        mMapView?.map?.animateMapStatus(mapStatusUpdate)
                    }
                }
            }
        }//消息接受到此结束


        override fun connectionLost(cause: Throwable?) {
            // 在此处理连接丢失的情况，可以进行重连等操作
        }

        override fun deliveryComplete(token: IMqttDeliveryToken?) {
            // 在此处理消息传递完成后的操作
        }
    }

    fun showBottomSheetDialog() {   //室内地图，用到了类似于短视频评论区的控件BottomSheetDialog
        val context = requireContext()

        // 检查上下文是否为 null
        if (context != null) {
            val bottomSheetDialog = BottomSheetDialog(context)

            // 使用正确的上下文获取 layoutInflater
            val inflater = requireActivity().layoutInflater
            val view = inflater.inflate(R.layout.bottom_sheet_dialog, null)

            // 获取底部对话框中的元素
            //val textView = view.findViewById<TextView>(R.id.textview)

            // 设置底部对话框的内容
            // textView.text = "This is a text ."

            bottomSheetDialog.setContentView(view)
            bottomSheetDialog.show()
        }
    }

    //地图中缩小图标icon的方法
    private fun createSmallIcon2(): BitmapDescriptor {

        val largeIcon2 = BitmapFactory.decodeResource(resources, R.drawable.oldman)//原素材
        val smallIcon2 = Bitmap.createScaledBitmap(largeIcon2, 50, 50, true)

        return BitmapDescriptorFactory.fromBitmap(smallIcon2)
    }


    fun hideStatusBar3() { //隐藏状态栏的方法
        // 获取关联的 Activity（在fragment中需要这样才能获取window对象）
        val activity = requireActivity()

        // 获取 Activity 的 Window 对象
        val window = activity.window

        WindowInsetsControllerCompat(window, window.decorView).let {
            // 隐藏状态栏
            it.hide(WindowInsetsCompat.Type.statusBars())
            // 维持隐藏的效果，效果同 View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            it.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }

        // 允许window 的内容可以上移到刘海屏状态栏
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val lp = window.attributes
            lp.layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            window.attributes = lp

            // 设置显示内容上移，适用于 Android R 及以上版本
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                window.setDecorFitsSystemWindows(false)
            } else {
                // 在 Android Q 及以下版本，使用系统标志设置
                window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            }
        }
    }
}
