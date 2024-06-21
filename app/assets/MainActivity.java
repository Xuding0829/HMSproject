
package com.example.location;
 
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import com.baidu.location.BDLocation;
import com.baidu.location.BDLocationListener;
import com.baidu.location.LocationClient;
import com.baidu.location.LocationClientOption;
import com.baidu.mapapi.SDKInitializer;
import com.baidu.mapapi.map.BaiduMap;
import com.baidu.mapapi.map.BitmapDescriptor;
import com.baidu.mapapi.map.BitmapDescriptorFactory;
import com.baidu.mapapi.map.MapStatusUpdate;
import com.baidu.mapapi.map.MapStatusUpdateFactory;
import com.baidu.mapapi.map.MapView;
import com.baidu.mapapi.map.MarkerOptions;
import com.baidu.mapapi.model.LatLng;
import com.baidu.mapapi.search.core.SearchResult;
import com.baidu.mapapi.search.geocode.GeoCodeOption;
import com.baidu.mapapi.search.geocode.GeoCodeResult;
import com.baidu.mapapi.search.geocode.GeoCoder;
import com.baidu.mapapi.search.geocode.OnGetGeoCoderResultListener;
import com.baidu.mapapi.search.geocode.ReverseGeoCodeResult;
 
public class MainActivity extends AppCompatActivity {
    LocationClient mLocationClient;
 
    MapView mMapView;
    BaiduMap mBaiduMap;
    private Button select;
    private EditText editText;
    boolean isFirstLocate = true;
    boolean isFirstText = true;
    TextView tv_Lat; // 经度
    TextView tv_Lon; // 纬度
    TextView tv_Add; // 地址
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // 初始化地图应用
        SDKInitializer.setAgreePrivacy(this.getApplicationContext(),true);
        LocationClient.setAgreePrivacy(true);
        SDKInitializer.initialize(this.getApplicationContext());
        setContentView(R.layout.activity_main);
        mMapView = findViewById(R.id.bmapView);
        mBaiduMap = mMapView.getMap();
        tv_Lat = findViewById(R.id.tv_Lat);
        tv_Lon = findViewById(R.id.tv_Lon);
        tv_Add = findViewById(R.id.tv_Add);
        select = findViewById(R.id.btn_search);
        editText = findViewById(R.id.address);
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)!= PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.ACCESS_FINE_LOCATION},1);
        }else {
            requestLocation();
        }
 
        select.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String address = editText.getText().toString();
                if (address!=null){
 
                    searchGeoCode(address);
                }else {
                    Toast.makeText(MainActivity.this, "请输入地点", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
 
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        switch (requestCode){
            case 1:
                if (grantResults[0]!=PackageManager.PERMISSION_GRANTED){
                    Toast.makeText(this, "没有定位权限！", Toast.LENGTH_SHORT).show();
                    finish();
                }else{
                        requestLocation();
                }
        }
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
 
    }
 
    private void requestLocation() {
         // 定位前初始化
        initLocation();
        // 发起定位
        mLocationClient.start();
    }
 
    private void initLocation() {
//        LocationClient.setAgreePrivacy(true);
        try {
            mLocationClient = new LocationClient(getApplicationContext());
            mLocationClient.registerLocationListener(new MyLocationListener());
 
            // 定位客户端操作
            LocationClientOption option = new LocationClientOption();
            // 设置扫描时间
            option.setScanSpan(1000);
            // 设置定位参数
            option.setCoorType("bd09ll"); // 设置坐标类型为百度经纬度
            option.setIsNeedAddress(true); // 设置需要获取地址信息
            // 设置定位模式
            option.setLocationMode(LocationClientOption.LocationMode.Hight_Accuracy);
//            option.setLocationMode(LocationClientOption.LocationMode.Battery_Saving);
//            option.setLocationMode(LocationClientOption.LocationMode.Device_Sensors);
            option.setIsNeedAddress(true); // 设置需要地址信息
            // 保存定位参数
            mLocationClient.setLocOption(option);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    // 内部类，百度位置监听器
    private class MyLocationListener implements BDLocationListener{
 
        @Override
        public void onReceiveLocation(BDLocation bdLocation) {
            if (isFirstText){
                tv_Lat.setText(bdLocation.getLatitude()+"");
                tv_Lon.setText(bdLocation.getLongitude()+"");
                tv_Add.setText(bdLocation.getAddrStr());
                isFirstText = false;
            }
            // GPS 定位或网格定位时
            if (bdLocation.getLocType()==BDLocation.TypeGpsLocation||bdLocation.getLocType()==BDLocation.TypeNetWorkLocation){
                navigateTo(bdLocation);
            }
        }
 
        private void navigateTo(BDLocation bdLocation) {
            if (isFirstLocate){
                LatLng ll = new LatLng(bdLocation.getLatitude(),bdLocation.getLongitude());
                MapStatusUpdate update = MapStatusUpdateFactory.newLatLng(ll);
                // 以动画更新方式，实现对手势引起的地图状态的更新
                mBaiduMap.animateMapStatus(update);
                // 创建自定义标记
                BitmapDescriptor bitmap = BitmapDescriptorFactory.fromResource(R.drawable.arrow_icon);
                MarkerOptions markerOptions = new MarkerOptions().position(ll).icon(bitmap).anchor(0.5f, 0.5f);
                mBaiduMap.addOverlay(markerOptions);
 
                isFirstLocate = false;
            }
        }
    }
 
    @Override
    protected void onResume() {
        super.onResume();
        mMapView.onResume();
    }
    // 实现检索地点功能
    private void searchGeoCode(String address) {
        mBaiduMap.clear(); // 清除标记点
 
        GeoCoder geoCoder = GeoCoder.newInstance();
        GeoCodeOption geoCodeOption = new GeoCodeOption();
        geoCodeOption.address(address);
        geoCodeOption.city(address);
        geoCoder.setOnGetGeoCodeResultListener(new OnGetGeoCoderResultListener() {
            @Override
            public void onGetGeoCodeResult(GeoCodeResult geoCodeResult) {
                if (geoCodeResult == null || geoCodeResult.error != SearchResult.ERRORNO.NO_ERROR) {
                    Toast.makeText(MainActivity.this, "检索错误", Toast.LENGTH_SHORT).show();
                } else {
                    LatLng latLng = geoCodeResult.getLocation();
                    MarkerOptions markerOptions = new MarkerOptions()
                            .position(latLng)
                            .icon(BitmapDescriptorFactory.fromResource(R.drawable.arrow_icon));
                    mBaiduMap.addOverlay(markerOptions);
                    MapStatusUpdate mMapStatusUpdate = MapStatusUpdateFactory.newLatLngZoom(latLng, 15);
                    tv_Lat.setText(" "+latLng.latitude); // 经度
                    tv_Lon.setText(" "+latLng.longitude); // 纬度
 
                    tv_Add.setText(geoCodeResult.getAddress()); // 地址
                    mBaiduMap.setMapStatus(mMapStatusUpdate);
 
                }
            }
            @Override
            public void onGetReverseGeoCodeResult(ReverseGeoCodeResult reverseGeoCodeResult) {
                if (reverseGeoCodeResult == null || reverseGeoCodeResult.error != SearchResult.ERRORNO.NO_ERROR) {
                    Toast.makeText(MainActivity.this, "获取地址信息失败", Toast.LENGTH_SHORT).show();
                } else {
                    String address = reverseGeoCodeResult.getAddress();
                    Toast.makeText(MainActivity.this, address, Toast.LENGTH_SHORT).show();
                }
            }
        });
        geoCoder.geocode(geoCodeOption);
    }
 
    @Override
    protected void onPause() {
        super.onPause();
        mMapView.onPause();
    }
 
    @Override
    protected void onDestroy() {
        super.onDestroy();
        mMapView.onDestroy();
    }
}