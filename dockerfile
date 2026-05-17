# ... (previous lines: FROM, WORKDIR, RUN pip install, etc.)

# 1. Copy the rest of the application code
COPY . .

# 2. ADD THIS LINE HERE
# It gives the app permission to save images to the static folder
RUN chmod -R 777 /app/static

# 3. Expose the port
EXPOSE 5000

# 4. The command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--preload", "app:app"]