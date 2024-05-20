package com.example.hmsproject.Utils

import com.baidu.location.BDAbstractLocationListener
import com.baidu.location.BDLocation
import com.baidu.location.LocationClient
import com.baidu.location.LocationClientOption
import com.baidu.mapapi.map.MapStatusUpdateFactory
import com.baidu.mapapi.map.MapView
import com.baidu.mapapi.map.MyLocationData
import com.baidu.mapapi.model.LatLng

class BaiduMapManager(private val mMapView: MapView) {
    private var mLocationClient: LocationClient? = null
    var currentLatitude: Double = 0.0
    var currentLongitude: Double = 0.0

    fun initialize() {
        // 初始化地图设置
        initMapSettings()

        // 初始化定位客户端
        mLocationClient = LocationClient(mMapView.context).apply {
            locOption = LocationClientOption().apply {
                isOpenGps = true
                coorType = "bd09ll"
                scanSpan = 1000
                locationMode = LocationClientOption.LocationMode.Hight_Accuracy
            }
            registerLocationListener(object : BDAbstractLocationListener() {
                override fun onReceiveLocation(location: BDLocation?) {
                    location?.let {
                        currentLatitude = it.latitude
                        currentLongitude = it.longitude
                        updateMapLocation()
                    }
                }
            })
        }
        mLocationClient?.start()
    }
    private fun initMapSettings() {
        // 在这里添加地图的初始化设置
        mMapView.map.isMyLocationEnabled = true
        // 其他地图设置...
    }

    private fun updateMapLocation() {
        // 更新地图位置逻辑

        // 构建当前位置的地图数据
        val locData = MyLocationData.Builder()
            .accuracy(100f) // 设置位置精度，以米为单位
            .direction(100f) // 设置方向角度，正北为0度
            .latitude(currentLatitude) // 设置纬度
            .longitude(currentLongitude) // 设置经度
            .build()

        // 将当前位置的地图数据应用到地图上
        mMapView.map.setMyLocationData(locData)

        // 构建地图状态的更新，以当前位置为中心，缩放级别为18
        val mapStatusUpdate = MapStatusUpdateFactory.newLatLngZoom(
            LatLng(currentLatitude, currentLongitude), // 设置地图中心点
            18f // 设置缩放级别
        )

        // 平滑动画显示更新后的地图状态
        mMapView.map.animateMapStatus(mapStatusUpdate)
    }



    fun onDestroy() {
        mLocationClient?.stop()
        mMapView.onDestroy()
    }

    fun onResume() {
        mMapView.onResume()
    }

    fun onPause() {
        mMapView.onPause()
    }
}
