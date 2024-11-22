package com.example.cse476exam_aaron_elkin;

import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class AccelerometerActivity extends AppCompatActivity implements SensorEventListener {

    private TextView mAccelerometerData;
    private Button mStartCaptureButton;
    private Button mStopCaptureButton;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;

    private Boolean mIsCapturing;
    private float[] currentPositionValues = new float[4];
    private Boolean mIsSaved = false;
    private Boolean mHasDataBeenCaptured = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_accelerometer);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        mAccelerometerData = findViewById(R.id.accelerometerData);
        mStartCaptureButton = findViewById(R.id.startCapture);
        mStopCaptureButton = findViewById(R.id.stopCapture);

        // Initialize sensor manager and accelerometer
        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

        mIsCapturing = false;

        // if there is no accelerometer then we can't capture anything
        if (mAccelerometer == null)
        {
            mAccelerometerData.setText(R.string.accelerometer_not_available_on_this_device);
            mStartCaptureButton.setEnabled(false);
            mStopCaptureButton.setEnabled(false);
        }

        // Load saved data for all states of this activity
        if (savedInstanceState != null) {
            currentPositionValues = savedInstanceState.getFloatArray("currentPositionValues");
            mIsCapturing = savedInstanceState.getBoolean("isCapturing");
            updateAccelerometerDataUI();

            // Was it already capturing the acceleration data
            if (mIsCapturing) {
                startCapture();
            }

            // Was the save button already clicked
            mIsSaved = savedInstanceState.getBoolean("isSaved");
            if (mIsSaved)
            {
                saveIntent();
            }
        }
    }

    private void saveIntent()
    {
        // Saves all the values of the acceleration and magnitude to the intent for when
        // we go back to the main activity
        Intent intent = new Intent();
        intent.putExtra("x", currentPositionValues[0]);
        intent.putExtra("y", currentPositionValues[1]);
        intent.putExtra("z", currentPositionValues[2]);
        intent.putExtra("amplitude", currentPositionValues[3]);
        setResult(RESULT_OK, intent);
    }
    public void onClickStartCapture(View view)
    {
        startCapture();
    }

    public void onClickStopCapture(View view)
    {
        stopCapture();
    }

    private void stopCapture() {
        // Unregisters the accelerometer listener only if it was already capturing data
        if (mIsCapturing) {
            mSensorManager.unregisterListener(this);
            mIsCapturing = false;
            Toast.makeText(this, R.string.capture_stopped, Toast.LENGTH_SHORT).show();
            mHasDataBeenCaptured = true;
        }
        else {
            Toast.makeText(this, R.string.no_capture_to_stop, Toast.LENGTH_SHORT).show();
        }
    }

    public void onClickSave(View view)
    {
        // If no data has been captured and if it is not currently capturing data then
        // there is nothing to save
        if (!mHasDataBeenCaptured && !mIsCapturing) {
            Toast.makeText(this, R.string.no_data_captured, Toast.LENGTH_SHORT).show();
            return;
        }
        saveIntent();
        mIsSaved = true;
        Toast.makeText(this, R.string.data_saved_successfully, Toast.LENGTH_SHORT).show();
    }

    public void onClickBack(View view)
    {
        stopCapture();
        finish();
    }

    private void updateAccelerometerDataUI() {
        mAccelerometerData.setText(getString(
                R.string.acceleration_values_x_2f_y_2f_z_2f_amplitude_2f,
                currentPositionValues[0],
                currentPositionValues[1],
                currentPositionValues[2],
                currentPositionValues[3]
        ));
    }

    private void startCapture() {
        if (mAccelerometer != null && !mIsCapturing) {
            mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_NORMAL);
            mIsCapturing = true;
            Toast.makeText(this, "Capture started.", Toast.LENGTH_SHORT).show();
        } else if (mIsCapturing) {
            Toast.makeText(this, "Already capturing.", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            float x = event.values[0];
            float y = event.values[1];
            float z = event.values[2];
            // magnitude of acceleration is sqrt(x^2 + y^2 + z^2)
            float amplitude = (float) Math.sqrt(x * x + y * y + z * z);

            currentPositionValues[0] = x;
            currentPositionValues[1] = y;
            currentPositionValues[2] = z;
            currentPositionValues[3] = amplitude;

            mAccelerometerData.setText(String.format(getString(R.string.acceleration_values_x_2f_y_2f_z_2f_amplitude_2f), x, y, z, amplitude));
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putFloatArray("currentPositionValues", currentPositionValues);
        outState.putBoolean("isCapturing", mIsCapturing);
        outState.putBoolean("isSaved", mIsSaved);
    }
    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {
        // Had to implement this override but nothing is needed here
    }
}
