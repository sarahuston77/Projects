package com.example.cse476exam_aaron_elkin;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.bumptech.glide.Glide;

public class MainActivity extends AppCompatActivity {
    private TextView mPlaceholderText;
    private ImageView mPlaceholderImage;
    private Boolean mIsImageDisplayed;
    private String mAccelerometerText;
    private String mImageUrl;

    // Result launcher for the accelerometer activity
    private final ActivityResultLauncher<Intent> accelerometerFetchingLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    accelerometerResultHandler(result);
                }
            }
    );

    // Result launcher for the image activity
    private final ActivityResultLauncher<Intent> imageLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    handleImageResult(result);
                }
            }
    );

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        mPlaceholderText = findViewById(R.id.placeholderText);
        mPlaceholderImage = findViewById(R.id.placeholderImage);
        mIsImageDisplayed = false;

        if (savedInstanceState != null) {
            // Loads the previous state, was an image or text previously displayed
            mAccelerometerText = savedInstanceState.getString("accelerometerText", null);
            mImageUrl = savedInstanceState.getString("imageUrl", null);
            mIsImageDisplayed = savedInstanceState.getBoolean("isDisplayingImage", false);

            // If there was an image, display it, if not then display the accelerometer text
            // if there was anything, otherwise it will stay at displaying "Not set"
            if (mIsImageDisplayed) {
                showImage(mImageUrl);
            } else if (mAccelerometerText != null) {
                showAccelerometerData(mAccelerometerText);
            }
        }
    }

    private void showImage(String imageUrl) {
        mIsImageDisplayed = true;
        mImageUrl = imageUrl;
        Glide.with(this)
                .load(imageUrl)
                .error(R.drawable.error_circle_fail_failure_disallowed_x_cross_bad_svgrepo_com) // Optional error image
                .into(mPlaceholderImage);

        //If the image is being displayed, it will remove the visibility of the text
        mPlaceholderImage.setVisibility(View.VISIBLE);
        mPlaceholderText.setVisibility(View.GONE);
    }

    private void showAccelerometerData(String text) {
        mIsImageDisplayed = false;
        mAccelerometerText = text;
        mPlaceholderText.setText(text);

        //If the text is being displayed it will remove the visibility of the image
        mPlaceholderText.setVisibility(View.VISIBLE);
        mPlaceholderImage.setVisibility(View.GONE);
    }

    private void handleImageResult(ActivityResult result) {
        Intent data = result.getData();
        String imageUrl = data.getStringExtra("imageUrl");

        // If a url was returned from the image activity, display it
        if (imageUrl != null) {
            showImage(imageUrl);
        }
    }

    private void accelerometerResultHandler(ActivityResult result)
    {
        // This is handled slightly different than the image, if there was no saved data, then
        // the return code wouldn't allow the result handler to reach this function
        Intent data = result.getData();
        float x = data.getFloatExtra("x", 0);
        float y = data.getFloatExtra("y", 0);
        float z = data.getFloatExtra("z", 0);
        float amplitude = data.getFloatExtra("amplitude", 0);

        String formattedData = getString(
                R.string.acceleration_values_x_2f_y_2f_z_2f_amplitude_2f,
                x, y, z, amplitude
        );

        showAccelerometerData(formattedData);
    }

    public void onClickImageButton(View view) {
        Intent intent = new Intent(this, ImageActivity.class);
        imageLauncher.launch(intent);
    }

    public void onClickTextButton(View view) {
        Intent intent = new Intent(this, AccelerometerActivity.class);
        accelerometerFetchingLauncher.launch(intent);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);

        outState.putString("accelerometerText", mAccelerometerText);
        outState.putString("imageUrl", mImageUrl);
        outState.putBoolean("isDisplayingImage", mIsImageDisplayed);
    }
}