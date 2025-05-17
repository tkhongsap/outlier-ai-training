import styles from '../profile/Profile.module.css';

const ProfileCard = ({ user, onEdit }) => {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h2>{user.name}</h2>
        <button 
          className={styles.editButton}
          onClick={onEdit}
        >
          Edit Profile
        </button>
      </div>
      <div className={styles.details}>
        <div className={styles.field}>
          <label>Email:</label>
          <p>{user.email}</p>
        </div>
        <div className={styles.field}>
          <label>Bio:</label>
          <p>{user.bio}</p>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard; 