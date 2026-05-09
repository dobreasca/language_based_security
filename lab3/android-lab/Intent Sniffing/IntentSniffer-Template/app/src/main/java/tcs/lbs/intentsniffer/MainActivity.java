package tcs.lbs.intentsniffer;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Build;
import android.widget.TextView;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.location.Location;

public class MainActivity extends AppCompatActivity
{
    TextView LatitudeTextView, LongitudeTextView;

    SnifferReceiver sniffer;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        LatitudeTextView = findViewById(R.id.LatitudeTextView);
        LongitudeTextView = findViewById(R.id.LongitudeTextView);

    }

    @Override
    protected void onResume() {
        super.onResume();

        IntentFilter broadcastFilter = new IntentFilter();

        broadcastFilter.addAction("tcs.lbs.locationapp.MainActivityReceiver");
        broadcastFilter.addAction("tcs.lbs.weather_app.WeatherBroadcastReceiver");

        sniffer = new SnifferReceiver();

        registerReceiver(sniffer, broadcastFilter, Context.RECEIVER_EXPORTED);

    }

    @Override
    protected void onPause() {
        super.onPause();
        if (sniffer != null) {
            unregisterReceiver(sniffer);
        }
    }

    public class SnifferReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            Location interceptedLocation = intent.getParcelableExtra("Location");

            if (interceptedLocation != null) {
                LatitudeTextView.setText("Lat: " + interceptedLocation.getLatitude());
                LongitudeTextView.setText("Lon: " + interceptedLocation.getLongitude());
            }
        }
    }

}
