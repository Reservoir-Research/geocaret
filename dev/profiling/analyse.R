options(tidyverse.quiet = TRUE)
options(lubridate.quiet = TRUE)
library(tidyverse)
library(lubridate)

# This scripts examines the computational resources
# and calculation times for analysis of a single dam
# (GawLan, ID12)

# This data has been extracted from the earth engine queue,
# so tells us about resource use and performance on EE 

# GawLan analysis (Nov 2022)
# Batch size 1
df_tasks_nov1 <- 
  read_csv("data/MYANMAR02_20221102-1408/tasks.csv", show_col_types = FALSE) %>%
  mutate(batch = "nov") %>%
  mutate(batch_size = 1) %>%
  mutate(batch_id = 1)

# Batch size 2
df_tasks_nov2 <- 
  read_csv("data/MYANMAR03_20221102-1511/tasks.csv", show_col_types = FALSE) %>%
  mutate(batch = "nov") %>%
  mutate(batch_size = 2) %>%
  mutate(batch_id = 2)


# Batch size 4
df_tasks_nov4 <- 
  read_csv("data/MYANMAR04_20221102-1549/tasks.csv", show_col_types = FALSE) %>%
  mutate(batch = "nov") %>%
  mutate(batch_size = 4) %>%
  mutate(batch_id = 4)

# Batch size 8
df_tasks_nov8 <- 
  read_csv("data/MYANMAR08_20221102-1639/tasks.csv", show_col_types = FALSE) %>%
  mutate(batch = "nov") %>%
  mutate(batch_size = 8) %>%
  mutate(batch_id = 8)

# Batch size 16
df_tasks_nov16 <- 
  read_csv("data/MYANMAR16_20221102-1755/tasks.csv", show_col_types = FALSE) %>%
  mutate(batch = "nov") %>%
  mutate(batch_size = 16) %>%
  mutate(batch_id = 16)

# Batch size 32
df_tasks_nov32 <- 
  read_csv("data/MYANMAR1_20221103-1044/tasks.csv", show_col_types = FALSE) %>%
  mutate(batch = "nov") %>%
  mutate(batch_size = 32) %>%
  mutate(batch_id = 32)


df_tasks <- 
  bind_rows( 
    df_tasks_nov1,
    df_tasks_nov2,
    df_tasks_nov4,
    df_tasks_nov8,
    df_tasks_nov16,
    df_tasks_nov32    
  ) 

df_tasks_prepared <- 
  df_tasks %>%
  mutate(queue_time = (start_timestamp_ms - creation_timestamp_ms)/1000) %>%
  mutate(run_time = (update_timestamp_ms - start_timestamp_ms)/1000) %>%
  mutate(job_time = (update_timestamp_ms - creation_timestamp_ms)/1000) %>%  
  mutate(fmt_queue_time = seconds_to_period((start_timestamp_ms - creation_timestamp_ms)/1000)) %>%
  mutate(fmt_run_time = seconds_to_period((update_timestamp_ms - start_timestamp_ms)/1000)) %>%
  group_by(batch_id) %>%
    mutate(run_time_rank = rank(-run_time)) %>%
    mutate(queue_time_rank = rank(-queue_time)) %>%
    mutate(eecu_time_rank = rank(-batch_eecu_usage_seconds)) %>%
    mutate(total_time = (max(update_timestamp_ms) - min(creation_timestamp_ms))/1000) %>%
    mutate(mean_time = (total_time/batch_size)) %>%
  ungroup() %>%
  mutate(step_name = paste(task_code, key, sep = "_")) %>%
  group_by(batch_id, task_code) %>%
    mutate(total_run_time = sum(run_time)) %>%
  ungroup() 
  
  
  

  
#====================================================
# Which tasks have the longest run-times
#====================================================
p_runtime <- df_tasks_prepared %>% 
  filter(batch_id == 1) %>% 
  ggplot(aes(x = run_time_rank, y = run_time, label = step_name)) +
  geom_point() +
  geom_text(hjust=0, vjust=0, angle = -90, size = 2) +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Run Time (s)",
    x = "Run Time Rank"
  )
  
p_queuetime <- df_tasks_prepared %>% 
  filter(batch_id == 1) %>% 
  ggplot(aes(x = queue_time_rank, y = queue_time, label = step_name)) +
  geom_point() +
  geom_text(hjust=0, vjust=0, angle = -90, size = 2) +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Queue Time (s)",
    x = "Queue Time Rank"
  )

p_eecu <- df_tasks_prepared %>% 
  filter(batch_id == 1) %>% 
  ggplot(aes(x = eecu_time_rank, y = batch_eecu_usage_seconds, label = step_name)) +
  geom_point() +
  geom_text(hjust=0, vjust=0, angle = -90, size = 2) +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Batch Compute Usage (s)",
    x = "Run Time Rank"
  )  

# Effect of batch size on task run-time
p_batchsize_runtime <- df_tasks_prepared %>% 
  filter(batch == "nov") %>% 
  ggplot(aes(x = batch_size, y = run_time)) +
  geom_point() +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Run Time (s)",
    x = "Batch Size"
  ) + 
  facet_wrap(~task_code)

# Effect of batch size on task queue-time
p_batchsize_queuetime <- df_tasks_prepared %>% 
  filter(batch == "nov") %>% 
  ggplot(aes(x = batch_size, y = queue_time)) +
  geom_point() +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Queue Time (s)",
    x = "Batch Size"
  ) + 
  facet_wrap(~task_code)

# Effect of batch size on task queue-time
p_batchsize_jobtime <- df_tasks_prepared %>% 
  filter(batch == "nov") %>% 
  ggplot(aes(x = batch_size, y = job_time)) +
  geom_point() +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Job Time (s)",
    x = "Batch Size"
  ) + 
  facet_wrap(~task_code)

p_batchsize_ecu <- df_tasks_prepared %>% 
  filter(batch == "nov") %>% 
  ggplot(aes(x = batch_size, y = batch_eecu_usage_seconds)) +
  geom_point() +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "ECU Run Time (s)",
    x = "Batch Size"
  ) + 
  facet_wrap(~task_code)

# Batch size and export time
p_batchsize_exporttime <- df_tasks_prepared %>% 
  filter(task_code == "drive_export") %>%
  filter(batch == "nov") %>% 
  distinct() %>%
  ggplot(aes(x = batch_size, y = total_run_time)) +
  geom_point() +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Export Time (s)",
    x = "Batch Size"
  ) + 
  facet_wrap(~task_code)

# Batch size and total time
p_batchsize_totaltime <- df_tasks_prepared %>% 
  filter(batch == "nov") %>% 
  select(batch_size, total_time, mean_time) %>%
  distinct() %>%
  ggplot(aes(x = batch_size, y = total_time)) +
  geom_point() +
  geom_point(aes(x = batch_size, y = mean_time), color = "blue") +
  geom_hline(yintercept=10, linetype="dashed", color = "purple") +
  geom_hline(yintercept=30, linetype="dashed", color = "green") +
  geom_hline(yintercept=60, linetype="dashed", color = "orange") +
  geom_hline(yintercept=120, linetype="dashed", color = "red") +
  ylim(-25,NA) +
  labs(
    y = "Total Time (s)",
    x = "Batch Size"
  )

